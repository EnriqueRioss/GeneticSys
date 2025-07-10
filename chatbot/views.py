# chatbot/views.py

import os
import re
import json
import traceback
from django.http import JsonResponse
from django.urls import reverse, NoReverseMatch
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.cache import cache
from django.conf import settings

import google.generativeai as genai
from google.generativeai.types import content_types
from dotenv import load_dotenv

from serpapi import SerpApiClient

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

from myapp.models import (
    Propositos, HistoriasClinicas, Genetistas, Parejas, InformacionPadres,
    ExamenFisico, AntecedentesPersonales, AntecedentesFamiliaresPreconcepcionales,
    PeriodoNeonatal, DesarrolloPsicomotor, EvaluacionGenetica,
    DiagnosticoPresuntivo, PlanEstudio
)
from .models import ChatInteraction

def debug_print(message):
    """Imprime mensajes de debug de forma destacada en la consola."""
    print(f"\n===== CHATBOT DEBUG =====\n{message}\n=======================\n")

load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
if google_api_key:
    debug_print(f"Google API Key Loaded: {google_api_key[:5]}...")
    try:
        genai.configure(api_key=google_api_key)
    except Exception as e:
        debug_print(f"Error crítico al configurar Gemini: {e}")
else:
    debug_print("GOOGLE_API_KEY NOT FOUND. Please check your .env file.")

# ==============================================================================
# === DECLARACIÓN DE HERRAMIENTAS PARA EL MODELO DE IA =========================
# ==============================================================================

def buscar_paciente(nombre_o_id: str) -> str:
    """Busca UN paciente por nombre, apellido o ID y devuelve un resumen completo de su historia clínica, incluyendo antecedentes, examen físico, diagnósticos y planes de estudio. Úsalo para resúmenes o detalles de un individuo o pareja."""
    pass

def listar_entidades(tipo_entidad: str) -> str:
    """Lista entidades generales como 'doctores' o 'pacientes recientes'."""
    pass

def buscar_pacientes_por_estado(estado: str) -> str:
    """Busca y lista TODOS los pacientes que coinciden con un estado como 'activo', 'inactivo' o 'en seguimiento'."""
    pass

def generar_enlace_pdf_paciente(nombre_o_id_paciente: str) -> str:
    """Genera un enlace PDF para la historia clínica de UN paciente específico. Preferiblemente usar el ID del paciente."""
    pass

def buscar_en_la_web(query: str) -> str:
    """Busca en la web información no relacionada con los pacientes de la clínica ni con el uso de la aplicación."""
    pass

def consultar_documentacion_app(pregunta_del_usuario: str) -> str:
    """Busca en la documentación interna para responder preguntas sobre CÓMO USAR la aplicación, qué significan los roles, cuál es el flujo de trabajo, etc. Es la herramienta principal para preguntas de 'cómo', 'dónde', 'qué es' o 'cuál es el proceso'."""
    pass

# ==============================================================================
# === LÓGICA INTERNA DE LAS HERRAMIENTAS (CON IMPLEMENTACIÓN) ===================
# ==============================================================================

def _get_pacientes_permitidos_for_user(user):
    try:
        user_profile = user.genetistas
        base_qs = Propositos.objects.select_related('historia__genetista__user').filter(historia__isnull=False)
        if user_profile.rol == 'ADM': return base_qs
        if user_profile.rol == 'GEN': return base_qs.filter(historia__genetista=user_profile)
        if user_profile.rol == 'LEC' and user_profile.associated_genetista:
            return base_qs.filter(historia__genetista=user_profile.associated_genetista)
        return Propositos.objects.none()
    except Genetistas.DoesNotExist:
        return Propositos.objects.none()

def _internal_buscar_paciente(consulta_especifica: str, user) -> dict:
    try:
        pacientes_permitidos_qs = _get_pacientes_permitidos_for_user(user)
        todos_los_pacientes_qs = Propositos.objects.all()
        paciente = None
        id_match = re.search(r'\b(\d+)\b', consulta_especifica)
        
        if id_match:
            paciente_id = id_match.group(1)
            paciente_encontrado = todos_los_pacientes_qs.filter(identificacion=paciente_id).first()
            if paciente_encontrado:
                if pacientes_permitidos_qs.filter(pk=paciente_encontrado.pk).exists():
                    paciente = paciente_encontrado
                else:
                    return {"error": f"El paciente con ID {paciente_id} existe, pero no tienes permisos para acceder a su información."}
        
        if not paciente:
            terms = [t for t in consulta_especifica.lower().split() if t not in {'de', 'el', 'la', 'un', 'resumen', 'info'}]
            if not terms: return {"error": "Por favor, proporciona un nombre, apellido o ID para la búsqueda."}
            q_obj = Q()
            for term in terms: q_obj &= (Q(nombres__icontains=term) | Q(apellidos__icontains=term))
            resultados = pacientes_permitidos_qs.filter(q_obj)
            if resultados.count() == 1: paciente = resultados.first()
            elif resultados.count() > 1: return {"error": f"Búsqueda ambigua. Múltiples pacientes encontrados: {', '.join([p.nombres for p in resultados])}."}
        
        if not paciente: return {"error": f"No se encontró ningún paciente que coincida con '{consulta_especifica}'."}

        historia = paciente.historia
        resultado_final = {
            "datos_personales": {
                "id": paciente.identificacion,
                "nombre_completo": f"{paciente.nombres} {paciente.apellidos}",
                "sexo": paciente.get_sexo_display() or "No registrado",
                "fecha_nacimiento": paciente.fecha_nacimiento.strftime('%d/%m/%Y') if paciente.fecha_nacimiento else "No registrado",
                "edad": f"{paciente.edad} años" if paciente.edad is not None else "No registrada",
                "genetista_asignado": historia.genetista.user.get_full_name() if historia and historia.genetista else "No asignado"
            },
            "datos_pareja": "No registrados.", "datos_padres": "No registrados.",
            "antecedentes_familiares": {}, "antecedentes_personales_y_desarrollo": {},
            "examen_fisico": {}, "evaluacion_genetica": {}
        }
        
        pareja = Parejas.objects.filter(Q(proposito_id_1=paciente) | Q(proposito_id_2=paciente)).select_related('proposito_id_1', 'proposito_id_2').first()
        if pareja:
            otro_conyuge = pareja.proposito_id_2 if pareja.proposito_id_1 == paciente else pareja.proposito_id_1
            resultado_final["datos_pareja"] = f"Cónyuge: {otro_conyuge.nombres} {otro_conyuge.apellidos} (ID: {otro_conyuge.identificacion})"
        else:
            padres = InformacionPadres.objects.filter(proposito=paciente)
            if padres.exists():
                resultado_final["datos_padres"] = {p.tipo: f"{p.nombres} {p.apellidos}" for p in padres}

        q_filter = Q(pareja=pareja) if pareja else Q(proposito=paciente)
        afp = AntecedentesFamiliaresPreconcepcionales.objects.filter(q_filter).first()
        if afp:
            resultado_final["antecedentes_familiares"] = {"consanguinidad": f"{afp.consanguinidad} ({afp.grado_consanguinidad})" if afp.consanguinidad == 'Sí' else "No", "maternos": afp.antecedentes_madre or "No registrados", "paternos": afp.antecedentes_padre or "No registrados"}
        ap = AntecedentesPersonales.objects.filter(q_filter).first()
        dp = DesarrolloPsicomotor.objects.filter(q_filter).first()
        pn = PeriodoNeonatal.objects.filter(q_filter).first()
        resultado_final["antecedentes_personales_y_desarrollo"] = {
            "complicaciones_embarazo": ap.complicaciones_embarazo if ap and ap.complicaciones_embarazo else "No especificadas",
            "hitos_desarrollo": f"Marcha: {dp.caminar if dp and dp.caminar else 'No reg.'}, Palabras: {dp.primeras_palabras if dp and dp.primeras_palabras else 'No reg.'}",
            "periodo_neonatal_peso_kg": pn.peso_nacer if pn and pn.peso_nacer is not None else "No registrado",
            "periodo_neonatal_talla_cm": pn.talla_nacer if pn and pn.talla_nacer is not None else "No registrado"
        }
        ef = ExamenFisico.objects.filter(proposito=paciente).first()
        if ef:
            resultado_final["examen_fisico"] = {"circ_cefalica_cm": ef.circunferencia_cefalica if ef.circunferencia_cefalica is not None else "No registrada", "peso_kg": ef.peso if ef.peso is not None else "No registrado", "talla_cm": ef.talla if ef.talla is not None else "No registrada", "observaciones_cabeza": ef.observaciones_cabeza or "Sin observaciones"}
        eval_genetica = EvaluacionGenetica.objects.filter(q_filter).first()
        if eval_genetica:
            diagnosticos = list(DiagnosticoPresuntivo.objects.filter(evaluacion=eval_genetica).order_by('orden').values_list('descripcion', flat=True))
            planes = list(PlanEstudio.objects.filter(evaluacion=eval_genetica).values('accion', 'completado'))
            resultado_final["evaluacion_genetica"] = {
                "diagnosticos_presuntivos": diagnosticos or ["Ninguno registrado"],
                "planes_de_estudio": [{p['accion']: "Completado" if p['completado'] else "Pendiente"} for p in planes] or ["Ninguno registrado"],
                "signos_clinicos": eval_genetica.signos_clinicos or "No registrados"
            }
        return resultado_final
    except Exception as e:
        debug_print(f"EXCEPCIÓN en _internal_buscar_paciente: {e}\n{traceback.format_exc()}"); 
        return {"error": "Error crítico al recopilar los datos del paciente."}

def _internal_listar_entidades(tipo_entidad: str, pacientes_permitidos_qs) -> dict:
    try:
        tipo_entidad = tipo_entidad.lower()
        if tipo_entidad in ['doctores', 'genetistas']:
            doctores = Genetistas.objects.filter(rol='GEN').select_related('user').order_by('user__last_name')
            return {"listado_doctores": [doc.user.get_full_name() or doc.user.username for doc in doctores]}
        if tipo_entidad in ['pacientes', 'pacientes_recientes', 'mis pacientes']:
            pacientes = pacientes_permitidos_qs.order_by('-historia__fecha_ingreso')[:10]
            if not pacientes.exists(): return {"error": "No se encontraron pacientes para tu perfil."}
            return {"listado_pacientes": [f"{p.nombres} {p.apellidos} (ID: {p.identificacion})" for p in pacientes]}
        return {"error": f"Tipo de entidad '{tipo_entidad}' no válido. Opciones: 'doctores', 'pacientes'."}
    except Exception as e:
        debug_print(f"EXCEPCIÓN en _internal_listar_entidades: {e}"); return {"error": "Error crítico al listar."}

def _internal_buscar_pacientes_por_estado(estado: str, pacientes_permitidos_qs) -> dict:
    try:
        estado_mapping = {'activo': 'activo', 'inactivo': 'inactivo', 'en seguimiento': 'en_seguimiento'}
        db_valor = estado_mapping.get(estado.lower().strip())
        if not db_valor: return {"error": "Estado no reconocido. Prueba con 'activo', 'inactivo' o 'en seguimiento'."}
        
        pacientes = pacientes_permitidos_qs.filter(estado=db_valor)
        if not pacientes.exists(): return {"mensaje": f"No se encontraron pacientes con estado '{estado}'."}
        return {f"pacientes_{estado.replace(' ','_')}": [f"{p.nombres} {p.apellidos}" for p in pacientes]}
    except Exception as e:
        debug_print(f"EXCEPCIÓN en _internal_buscar_pacientes_por_estado: {e}"); return {"error": "Error crítico buscando por estado."}

def _internal_generar_enlace_pdf(nombre_o_id: str, pacientes_permitidos_qs) -> dict:
    try:
        id_match = re.search(r'\b(\d+)\b', nombre_o_id)
        if not id_match: return {"error": "Por favor, proporciona el ID numérico del paciente para generar el PDF."}
        paciente = pacientes_permitidos_qs.filter(identificacion=id_match.group(1)).first()
        if not paciente: return {"error": f"No se encontró un paciente con ID '{id_match.group(1)}' en tus registros."}
        if not paciente.historia: return {"error": f"El paciente ID '{id_match.group(1)}' no tiene historia clínica para generar PDF."}

        url = reverse('myapp:historia_pdf', kwargs={'historia_id': paciente.historia.pk})
        return {"nombre_paciente": f"{paciente.nombres} {paciente.apellidos}", "url_descarga": url}
    except NoReverseMatch:
         debug_print("ERROR: NoReverseMatch. La URL para PDF en myapp/urls.py debe tener `name='historia_pdf'`")
         return {"error": "Error de configuración interna del servidor (URL PDF no encontrada)."}
    except Exception as e:
        debug_print(f"EXCEPCIÓN en _internal_generar_enlace_pdf: {e}"); return {"error": "Error crítico al generar enlace PDF."}

def _internal_buscar_web(query: str) -> dict:
    serpapi_key = os.getenv("SERPAPI_API_KEY")
    if not serpapi_key:
        debug_print("SERPAPI_API_KEY no encontrada en .env")
        return {"error": "El servicio de búsqueda web no está configurado."}
    
    params = {"q": query, "engine": "google", "api_key": serpapi_key}
    try:
        search = SerpApiClient(params)
        results = search.get_dict()
        if "error" in results: return {"error": f"SerpApi devolvió un error: {results['error']}"}
        organic_results = results.get("organic_results", [])
        if not organic_results: return {"web_search_summary": "No se encontraron resultados relevantes."}
        snippets = [r.get("snippet", "") for r in organic_results[:3] if r.get("snippet")]
        return {"web_search_summary": "\n\n".join(snippets)}
    except Exception as e:
        debug_print(f"EXCEPCIÓN en _internal_buscar_web: {e}\n{traceback.format_exc()}")
        return {"error": f"Error crítico durante la búsqueda web con SerpApi: {e}"}

def _internal_consultar_documentacion_app(query: str) -> dict:
    try:
        chroma_db_dir = os.path.join(settings.BASE_DIR, 'chatbot_docs', 'chroma_db')
        if not os.path.exists(chroma_db_dir):
            return {"error": "La base de conocimiento no ha sido creada. Ejecute 'python manage.py build_vector_db'."}
        embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = Chroma(persist_directory=chroma_db_dir, embedding_function=embeddings_model)
        retriever = vector_store.as_retriever(search_kwargs={'k': 4})
        relevant_docs = retriever.invoke(query)
        if not relevant_docs:
            return {"contexto": "No se encontró información relevante en la documentación."}
        context = "\n\n---\n\n".join([doc.page_content for doc in relevant_docs])
        return {"contexto_encontrado": context}
    except Exception as e:
        debug_print(f"EXCEPCIÓN en _internal_consultar_documentacion_app: {e}\n{traceback.format_exc()}"); 
        return {"error": "Error crítico al buscar en la base de conocimiento."}

# ==============================================================================
# === VISTA PRINCIPAL DEL CHATBOT ==============================================
# ==============================================================================
def get_bot_response(query: str, user) -> dict:
    session_key = f"chat_history_{user.id}"
    chat_history = cache.get(session_key, [])

    # <<< CAMBIO: System prompt mejorado para dar "libertad total" a la búsqueda web >>>
    system_prompt = f"""
    Eres GenAssist, un asistente experto de la aplicación GenClinic para el usuario '{user.username}'. Tu objetivo es ser proactivo y siempre encontrar una respuesta utilizando las herramientas a tu disposición.

    Tu proceso de decisión es el siguiente:
    1.  Primero, comprueba si la pregunta es MUY específica sobre **cómo usar la aplicación** (ej: "cómo creo un reporte", "dónde está el botón de registro"). Si es así, usa `consultar_documentacion_app`.
    2.  Luego, comprueba si la pregunta es MUY específica sobre **datos internos de la clínica** (ej: "info del paciente 12345", "lista de doctores"). Si es así, usa las herramientas de datos como `buscar_paciente`.

    3.  **Para TODO LO DEMÁS, tu acción por defecto e inmediata es `buscar_en_la_web`.** Esto incluye:
        - Definiciones de términos médicos o científicos (ADN, fenotipo, etc.).
        - Información sobre enfermedades o síndromes.
        - Cualquier pregunta general que no mencione explícitamente un paciente o una función de la app.

    Si tienes la más mínima duda sobre a qué categoría pertenece una pregunta, no dudes y utiliza `buscar_en_la_web`. Es mejor buscar que no responder. NUNCA respondas desde tu propio conocimiento.


    """

    if not google_api_key:
        return {'response': "El servicio de IA no está configurado (falta GOOGLE_API_KEY).", 'suggestions': []}

    try:
        tools_for_model = [
            buscar_paciente, listar_entidades, buscar_pacientes_por_estado, 
            generar_enlace_pdf_paciente, buscar_en_la_web, consultar_documentacion_app
        ]
        
        model = genai.GenerativeModel(
            'gemini-1.5-flash-latest', 
            system_instruction=system_prompt, 
            tools=tools_for_model
        )

        chat_session = model.start_chat(history=chat_history)
        response = chat_session.send_message(query)

        while response.candidates and response.candidates[0].content.parts and response.candidates[0].content.parts[0].function_call:
            function_call = response.candidates[0].content.parts[0].function_call
            function_name = function_call.name
            function_args = {key: value for key, value in function_call.args.items()}
            debug_print(f"Modelo quiere llamar a: {function_name} con argumentos: {function_args}")
            
            tool_result_obj = {}
            pacientes_permitidos = _get_pacientes_permitidos_for_user(user)

            if function_name == "consultar_documentacion_app":
                tool_result_obj = _internal_consultar_documentacion_app(function_args.get('pregunta_del_usuario', query))
            elif function_name == "buscar_paciente":
                tool_result_obj = _internal_buscar_paciente(function_args.get('nombre_o_id', ''), user)
            elif function_name == "listar_entidades":
                tool_result_obj = _internal_listar_entidades(function_args.get('tipo_entidad', ''), pacientes_permitidos)
            elif function_name == "buscar_pacientes_por_estado":
                tool_result_obj = _internal_buscar_pacientes_por_estado(function_args.get('estado', ''), pacientes_permitidos)
            elif function_name == "generar_enlace_pdf_paciente":
                 tool_result_obj = _internal_generar_enlace_pdf(function_args.get('nombre_o_id_paciente', ''), pacientes_permitidos)
            elif function_name == "buscar_en_la_web":
                tool_result_obj = _internal_buscar_web(function_args.get('query', ''))
            else:
                tool_result_obj = {"error": f"Herramienta desconocida: {function_name}"}

            debug_print(f"Resultado de la herramienta ({function_name}): {json.dumps(tool_result_obj, indent=2, default=str)}")
            
            response = chat_session.send_message(
                content_types.to_content(genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(name=function_name, response={"result": tool_result_obj})
                ))
            )
        
        response_text = "".join(part.text for part in response.candidates[0].content.parts) if response.candidates and response.candidates[0].content.parts else ""
        if not response_text.strip():
            debug_print(f"El modelo no devolvió una respuesta de texto. Respuesta completa: {response}")
            response_text = "No pude procesar la solicitud para generar una respuesta de texto. Por favor, intenta reformular tu pregunta."
        
        chat_history.append({'role': 'user', 'parts': [{'text': query}]})
        chat_history.append({'role': 'model', 'parts': [{'text': response_text}]})
        cache.set(session_key, chat_history, timeout=600)
        
        html_response = response_text.replace('\n', '<br>')
        html_response = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_response)
        html_response = re.sub(r'\* (.*?)(<br>|$)', r'<li>\1</li>', html_response)
        if '<li>' in html_response: html_response = f"<ul>{html_response.replace('<br>', '')}</ul>"

        return {'response': html_response, 'suggestions': []}

    except Exception as e:
        error_details = traceback.format_exc()
        debug_print(f"Error CRÍTICO en get_bot_response: {e}\n{error_details}")
        return {'response': "Lo siento, ha ocurrido un error inesperado en el asistente. El equipo técnico ha sido notificado.", 'suggestions': []}

# ==============================================================================
# === VISTA DE API (ENDPOINT DE DJANGO) ========================================
# ==============================================================================
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def chat_api(request):
    try:
        data = json.loads(request.body)
        query = data.get('query')
        if not query: return JsonResponse({'error': 'Falta la consulta (query).'}, status=400)
        bot_data = get_bot_response(query, request.user)
        ChatInteraction.objects.create(user=request.user, user_query=query, bot_response=bot_data.get('response', ''))
        return JsonResponse(bot_data)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Cuerpo de la petición inválido (no es JSON).'}, status=400)
    except Exception as e:
        debug_print(f"Error en la vista chat_api: {e}")
        return JsonResponse({'error': f'Error en el servidor: {e}'}, status=500)