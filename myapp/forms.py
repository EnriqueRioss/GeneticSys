# forms.py

from django import forms
from django.utils import timezone
from django.forms import ModelForm, Select, DateInput, ClearableFileInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime
from django.forms import inlineformset_factory, DateInput
import os


from .models import (
    HistoriasClinicas, Propositos, InformacionPadres, PeriodoNeonatal,
    AntecedentesFamiliaresPreconcepcionales, DesarrolloPsicomotor,
    AntecedentesPersonales, ExamenFisico, Parejas, EvaluacionGenetica, Genetistas,
    EvaluacionGenetica, DiagnosticoPresuntivo, PlanEstudio,Autorizaciones,ArchivoPlanEstudio
)

# --- General Purpose Forms ---

class CreateNewTask(forms.Form):
    title = forms.CharField(label="Title", max_length=200, strip=True)
    description = forms.CharField(label="Description", widget=forms.Textarea, strip=True)

class CreateNewProject(forms.Form):
    name = forms.CharField(label="Nombre Del Proyecto", max_length=200, strip=True)

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Username",
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        strip=True
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        strip=True
    )

class ExtendedUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.', strip=True)
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.', strip=True)
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Inform a valid email address.')
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

# --- Clinical History Related Forms ---

class HistoriasForm(ModelForm):
    class Meta:
        model = HistoriasClinicas
        fields = ['numero_historia', 'motivo_tipo_consulta', 'cursante_postgrado', 'medico', 'especialidad', 'centro_referencia']
        widgets = {
            'motivo_tipo_consulta': Select(attrs={'onchange': 'toggleForms()'}),
            'cursante_postgrado': forms.TextInput(attrs={'placeholder': 'Opcional'}),
            'medico': forms.TextInput(attrs={'placeholder': 'Opcional'}),
            'especialidad': forms.TextInput(attrs={'placeholder': 'Opcional'}),
            'centro_referencia': forms.TextInput(attrs={'placeholder': 'Opcional'}),
        }
        labels = {
            'numero_historia': "Número de Historia Único",
            'motivo_tipo_consulta': "Motivo/Tipo de Consulta",
            'cursante_postgrado': "Cursante de Postgrado (Si aplica)",
            'medico': "Médico Referente",
            'especialidad': "Especialidad del Médico Referente",
            'centro_referencia': "Centro de Referencia (Si aplica)",
        }

    def clean_numero_historia(self):
        numero_historia = self.cleaned_data.get('numero_historia')
        if numero_historia is not None and numero_historia <= 0:
            raise forms.ValidationError("El número de historia debe ser un valor positivo.")
        
        query = HistoriasClinicas.objects.filter(numero_historia=numero_historia)
        
        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        
        if query.exists():
            raise forms.ValidationError("Ya existe otra historia clínica con este número.")
            
        return numero_historia

class PadresPropositoForm(forms.Form):
    
    # ... (campos del padre y la madre se mantienen igual) ...
    padre_nombres = forms.CharField(max_length=100, label="Nombres del Padre", strip=True)
    padre_apellidos = forms.CharField(max_length=100, label="Apellidos del Padre", strip=True)
    padre_escolaridad = forms.CharField(max_length=100, required=False, label="Escolaridad del Padre", strip=True)
    padre_ocupacion = forms.CharField(max_length=100, required=False, label="Ocupación del Padre", strip=True)
    padre_lugar_nacimiento = forms.CharField(max_length=100, required=False, label="Lugar de Nacimiento del Padre", strip=True)
    padre_fecha_nacimiento = forms.DateField(
        required=False,
        widget=DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha de Nacimiento del Padre"
    )
    padre_edad = forms.IntegerField(required=False, label="Edad del Padre (años)", widget=forms.NumberInput(attrs={'min': '0', 'max': '120'}))
    padre_identificacion = forms.CharField(max_length=20, required=False, label="Identificación del Padre", strip=True)
    padre_grupo_sanguineo = forms.ChoiceField(
        choices=[('', 'Seleccione')] + InformacionPadres._meta.get_field('grupo_sanguineo').choices,
        required=False, label="Grupo Sanguíneo del Padre"
    )
    padre_factor_rh = forms.ChoiceField(
        choices=[('', 'Seleccione')] + InformacionPadres._meta.get_field('factor_rh').choices,
        required=False, label="Factor RH del Padre"
    )
    padre_telefono = forms.CharField(max_length=15, required=False, label="Teléfono del Padre", strip=True)
    padre_email = forms.EmailField(max_length=100, required=False, label="Email del Padre")
    padre_direccion = forms.CharField(max_length=200, required=False, label="Dirección del Padre", strip=True)

    madre_nombres = forms.CharField(max_length=100, label="Nombres de la Madre", strip=True)
    madre_apellidos = forms.CharField(max_length=100, label="Apellidos de la Madre", strip=True)
    madre_escolaridad = forms.CharField(max_length=100, required=False, label="Escolaridad de la Madre", strip=True)
    madre_ocupacion = forms.CharField(max_length=100, required=False, label="Ocupación de la Madre", strip=True)
    madre_lugar_nacimiento = forms.CharField(max_length=100, required=False, label="Lugar de Nacimiento de la Madre", strip=True)
    madre_fecha_nacimiento = forms.DateField(
        required=False,
        widget=DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha de Nacimiento de la Madre"
    )
    madre_edad = forms.IntegerField(required=False, label="Edad de la Madre (años)", widget=forms.NumberInput(attrs={'min': '0', 'max': '120'}))
    madre_identificacion = forms.CharField(max_length=20, required=False, label="Identificación de la Madre", strip=True)
    madre_grupo_sanguineo = forms.ChoiceField(
        choices=[('', 'Seleccione')] + InformacionPadres._meta.get_field('grupo_sanguineo').choices,
        required=False, label="Grupo Sanguíneo de la Madre"
    )
    madre_factor_rh = forms.ChoiceField(
        choices=[('', 'Seleccione')] + InformacionPadres._meta.get_field('factor_rh').choices,
        required=False, label="Factor RH de la Madre"
    )
    madre_telefono = forms.CharField(max_length=15, required=False, label="Teléfono de la Madre", strip=True)
    madre_email = forms.EmailField(max_length=100, required=False, label="Email de la Madre")
    madre_direccion = forms.CharField(max_length=200, required=False, label="Dirección de la Madre", strip=True)

    def __init__(self, *args, **kwargs):
        """
        Añadimos un __init__ para recibir las instancias del padre y la madre desde la vista.
        """
        self.padre_instance = kwargs.pop('padre_instance', None)
        self.madre_instance = kwargs.pop('madre_instance', None)
        super().__init__(*args, **kwargs)

    def clean_padre_identificacion(self):
        """
        Validación de unicidad para la identificación del padre, consciente del modo edición.
        """
        identificacion = self.cleaned_data.get('padre_identificacion', '').strip()
        if not identificacion:
            return identificacion # Es opcional, no validamos si está vacío

        query = InformacionPadres.objects.filter(identificacion=identificacion)
        if self.padre_instance and self.padre_instance.pk:
            query = query.exclude(pk=self.padre_instance.pk)
        
        if query.exists():
            raise forms.ValidationError("Ya existe una persona (padre/madre) con esta identificación.")
        
        return identificacion

    def clean_madre_identificacion(self):
        """
        Validación de unicidad para la identificación de la madre, consciente del modo edición.
        """
        identificacion = self.cleaned_data.get('madre_identificacion', '').strip()
        if not identificacion:
            return identificacion # Es opcional, no validamos si está vacío

        query = InformacionPadres.objects.filter(identificacion=identificacion)
        if self.madre_instance and self.madre_instance.pk:
            query = query.exclude(pk=self.madre_instance.pk)

        if query.exists():
            raise forms.ValidationError("Ya existe una persona (padre/madre) con esta identificación.")
            
        return identificacion

    def clean_padre_fecha_nacimiento(self):
        fecha = self.cleaned_data.get('padre_fecha_nacimiento')
        if fecha and fecha > timezone.now().date():
            raise forms.ValidationError("La fecha de nacimiento no puede ser en el futuro.")
        return fecha

    def clean_madre_fecha_nacimiento(self):
        fecha = self.cleaned_data.get('madre_fecha_nacimiento')
        if fecha and fecha > timezone.now().date():
            raise forms.ValidationError("La fecha de nacimiento no puede ser en el futuro.")
        return fecha

    def clean_padre_edad(self):
        edad = self.cleaned_data.get('padre_edad')
        if edad is not None and (edad < 0 or edad > 120):
            raise forms.ValidationError("Por favor, ingrese una edad válida (0-120 años).")
        return edad

    def clean_madre_edad(self):
        edad = self.cleaned_data.get('madre_edad')
        if edad is not None and (edad < 0 or edad > 120):
            raise forms.ValidationError("Por favor, ingrese una edad válida (0-120 años).")
        return edad

    def clean(self):
        cleaned_data = super().clean()
        padre_id = cleaned_data.get('padre_identificacion', '').strip()
        madre_id = cleaned_data.get('madre_identificacion', '').strip()

        if padre_id and madre_id and padre_id == madre_id:
            self.add_error('madre_identificacion', "La identificación de la madre no puede ser igual a la del padre.")
        return cleaned_data

class PropositosForm(ModelForm):
    """
    REESTRUCTURADO a ModelForm. Esto simplifica la vista y el manejo de instancias.
    """
    class Meta:
        model = Propositos
        # Excluimos los campos que se manejan automáticamente o en la vista.
        exclude = ['proposito_id', 'historia', 'estado'] 
        widgets = {
            'sexo': forms.Select,
            'fecha_nacimiento': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'edad': forms.NumberInput(attrs={'min': '0', 'max': '120'}),
            'foto': ClearableFileInput(attrs={'accept': 'image/*'}),
        }
        labels = {
            'nombres': "Nombres",
            'apellidos': "Apellidos",
            'sexo': "Sexo",
            'lugar_nacimiento': "Lugar de Nacimiento",
            'escolaridad': "Escolaridad",
            'ocupacion': "Ocupación",
            'edad': "Edad (años)",
            'fecha_nacimiento': "Fecha de Nacimiento",
            'identificacion': "Identificación (Cédula/Pasaporte)",
            'direccion': "Dirección",
            'telefono': "Teléfono",
            'email': "Email",
            'grupo_sanguineo': "Grupo Sanguíneo",
            'factor_rh': "Factor RH",
            'foto': 'Foto del Propósito (Opcional)'
        }

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get('fecha_nacimiento')
        if fecha and fecha > timezone.now().date():
            raise forms.ValidationError("La fecha de nacimiento no puede ser en el futuro.")
        return fecha

    def clean_edad(self):
        edad = self.cleaned_data.get('edad')
        if edad is not None and (edad < 0 or edad > 120):
            raise forms.ValidationError("Por favor, ingrese una edad válida (0-120 años).")
        return edad

    def clean_identificacion(self):
        """
        Esta es la validación clave, similar a la de HistoriasForm.
        """
        identificacion = self.cleaned_data.get('identificacion')
        if not identificacion:
            raise forms.ValidationError("La identificación es obligatoria.")

        query = Propositos.objects.filter(identificacion=identificacion)
        
        # Si el formulario está en modo edición (tiene una instancia),
        # excluimos a esa propia instancia de la búsqueda.
        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        
        # Si después de excluirla, todavía existe un resultado,
        # significa que OTRO propósito tiene esa identificación.
        if query.exists():
            raise forms.ValidationError("Ya existe un propósito con esta identificación.")
            
        return identificacion

    def save(self, commit=True, historia=None):
        """
        Sobrescribimos el save para asociar la historia clínica.
        """
        proposito = super().save(commit=False)
        
        if historia:
            proposito.historia = historia
            
        if commit:
            proposito.save()
            
        return proposito

class ParejaPropositosForm(forms.Form):
    # (Este formulario no cambia, ya que su vista 'crear_pareja' no tiene un modo de edición explícito.
    # La lógica de "editar" se maneja con `update_or_create` en la vista, lo cual es correcto para
    # encontrar y asociar propósitos existentes a una nueva pareja.)
    # Se deja el código original.
    nombres_1 = forms.CharField(max_length=100, label="Nombres (Primer Cónyuge)", strip=True)
    apellidos_1 = forms.CharField(max_length=100, label="Apellidos (Primer Cónyuge)", strip=True)
    sexo_1 = forms.ChoiceField(
        choices=[('', 'Seleccione')] + Propositos.SEXO_CHOICES,
        required=True, label="Sexo"
    )
    lugar_nacimiento_1 = forms.CharField(max_length=100, required=False, label="Lugar de Nacimiento", strip=True)
    fecha_nacimiento_1 = forms.DateField(required=False, widget=DateInput(attrs={'type': 'date', 'class': 'form-control'}), label="Fecha de Nacimiento")
    escolaridad_1 = forms.CharField(max_length=100, required=False, label="Escolaridad", strip=True)
    ocupacion_1 = forms.CharField(max_length=100, required=False, label="Ocupación", strip=True)
    edad_1 = forms.IntegerField(required=False, label="Edad (años)", widget=forms.NumberInput(attrs={'min':'0', 'max':'120'}))
    identificacion_1 = forms.CharField(max_length=20, label="Identificación", strip=True)
    direccion_1 = forms.CharField(max_length=200, required=False, label="Dirección", strip=True)
    telefono_1 = forms.CharField(max_length=15, required=False, label="Teléfono", strip=True)
    email_1 = forms.EmailField(max_length=100, required=False, label="Email")
    grupo_sanguineo_1 = forms.ChoiceField(choices=[('', 'Seleccione')] + Propositos._meta.get_field('grupo_sanguineo').choices, required=False, label="Grupo Sanguíneo")
    factor_rh_1 = forms.ChoiceField(choices=[('', 'Seleccione')] + Propositos._meta.get_field('factor_rh').choices, required=False, label="Factor RH")
    foto_1 = forms.ImageField(required=False, widget=ClearableFileInput(attrs={'accept': 'image/*'}), label="Foto (Opcional)")

    nombres_2 = forms.CharField(max_length=100, label="Nombres (Segundo Cónyuge)", strip=True)
    apellidos_2 = forms.CharField(max_length=100, label="Apellidos (Segundo Cónyuge)", strip=True)
    sexo_2 = forms.ChoiceField(
        choices=[('', 'Seleccione')] + Propositos.SEXO_CHOICES,
        required=True, label="Sexo"
    )
    lugar_nacimiento_2 = forms.CharField(max_length=100, required=False, label="Lugar de Nacimiento", strip=True)
    fecha_nacimiento_2 = forms.DateField(required=False, widget=DateInput(attrs={'type': 'date', 'class': 'form-control'}), label="Fecha de Nacimiento")
    escolaridad_2 = forms.CharField(max_length=100, required=False, label="Escolaridad", strip=True)
    ocupacion_2 = forms.CharField(max_length=100, required=False, label="Ocupación", strip=True)
    edad_2 = forms.IntegerField(required=False, label="Edad (años)", widget=forms.NumberInput(attrs={'min':'0', 'max':'120'}))
    identificacion_2 = forms.CharField(max_length=20, label="Identificación", strip=True)
    direccion_2 = forms.CharField(max_length=200, required=False, label="Dirección", strip=True)
    telefono_2 = forms.CharField(max_length=15, required=False, label="Teléfono", strip=True)
    email_2 = forms.EmailField(max_length=100, required=False, label="Email")
    grupo_sanguineo_2 = forms.ChoiceField(choices=[('', 'Seleccione')] + Propositos._meta.get_field('grupo_sanguineo').choices, required=False, label="Grupo Sanguíneo")
    factor_rh_2 = forms.ChoiceField(choices=[('', 'Seleccione')] + Propositos._meta.get_field('factor_rh').choices, required=False, label="Factor RH")
    foto_2 = forms.ImageField(required=False, widget=ClearableFileInput(attrs={'accept': 'image/*'}), label="Foto (Opcional)")

    def clean_fecha_nacimiento_1(self):
        fecha = self.cleaned_data.get('fecha_nacimiento_1')
        if fecha and fecha > timezone.now().date():
            raise forms.ValidationError("La fecha de nacimiento no puede ser en el futuro.")
        return fecha

    def clean_fecha_nacimiento_2(self):
        fecha = self.cleaned_data.get('fecha_nacimiento_2')
        if fecha and fecha > timezone.now().date():
            raise forms.ValidationError("La fecha de nacimiento no puede ser en el futuro.")
        return fecha

    def clean_edad_1(self):
        edad = self.cleaned_data.get('edad_1')
        if edad is not None and (edad < 0 or edad > 120):
            raise forms.ValidationError("Por favor, ingrese una edad válida (0-120 años).")
        return edad

    def clean_edad_2(self):
        edad = self.cleaned_data.get('edad_2')
        if edad is not None and (edad < 0 or edad > 120):
            raise forms.ValidationError("Por favor, ingrese una edad válida (0-120 años).")
        return edad

    def clean_identificacion_1(self):
        ident = self.cleaned_data.get('identificacion_1')
        if not ident:
            raise forms.ValidationError("La identificación del primer cónyuge es obligatoria.")
        return ident

    def clean_identificacion_2(self):
        ident = self.cleaned_data.get('identificacion_2')
        if not ident:
            raise forms.ValidationError("La identificación del segundo cónyuge es obligatoria.")
        return ident

    def clean(self):
        cleaned_data = super().clean()
        id_1 = cleaned_data.get('identificacion_1')
        id_2 = cleaned_data.get('identificacion_2')

        if id_1 and id_2 and id_1 == id_2:
            self.add_error('identificacion_2', "Las identificaciones de los cónyuges deben ser diferentes.")
        
        # Validación de unicidad para cada cónyuge, ya que la vista usa `update_or_create`.
        # Esto previene sobrescribir un propósito existente con datos nuevos si se ingresa su ID por error.
        # NOTA: Esto asume que si se ingresa una ID existente, los nombres deben coincidir.
        # Es una simplificación. La lógica robusta está en la vista.
        if id_1:
            if Propositos.objects.filter(identificacion=id_1).exists():
                pass # La vista se encargará de actualizar (update_or_create)
        if id_2:
            if Propositos.objects.filter(identificacion=id_2).exists():
                pass # La vista se encargará de actualizar (update_or_create)
                
        return cleaned_data

class AntecedentesDesarrolloNeonatalForm(forms.Form):
    fur = forms.DateField(required=False, widget=DateInput(attrs={'type': 'date', 'class':'form-control'}), label="Fecha de Última Regla (FUR)")
    edad_gestacional = forms.IntegerField(required=False, label="Edad Gestacional (semanas)", widget=forms.NumberInput(attrs={'min':'0'}))
    controles_prenatales = forms.CharField(max_length=100, required=False, label="Controles Prenatales", strip=True)
    numero_partos = forms.IntegerField(required=False, label="Número de Partos", widget=forms.NumberInput(attrs={'min':'0'}))
    numero_gestas = forms.IntegerField(required=False, label="Número de Gestas", widget=forms.NumberInput(attrs={'min':'0'}))
    numero_cesareas = forms.IntegerField(required=False, label="Número de Cesáreas", widget=forms.NumberInput(attrs={'min':'0'}))
    numero_abortos = forms.IntegerField(required=False, label="Número de Abortos", widget=forms.NumberInput(attrs={'min':'0'}))
    numero_mortinatos = forms.IntegerField(required=False, label="Número de Mortinatos", widget=forms.NumberInput(attrs={'min':'0'}))
    numero_malformaciones = forms.IntegerField(required=False, label="Número de Hijos con Malformaciones", widget=forms.NumberInput(attrs={'min':'0'}))
    complicaciones_embarazo = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}), label="Complicaciones en Embarazo(s)", strip=True)
    exposicion_teratogenos = forms.ChoiceField(
        choices=[('', '---------')] + AntecedentesPersonales._meta.get_field('exposicion_teratogenos').choices,
        required=False, label="Exposición a Teratógenos"
    )
    descripcion_exposicion = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}), label="Descripción de Exposición", strip=True)
    enfermedades_maternas = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}), label="Enfermedades Maternas", strip=True)
    complicaciones_parto = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}), label="Complicaciones en Parto(s)", strip=True)
    otros_antecedentes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}), label="Otros Antecedentes Personales", strip=True)
    observaciones = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}), label="Observaciones Generales (Personales)", strip=True)

    sostener_cabeza = forms.CharField(max_length=100, required=False, label="Sostén Cefálico (edad)", strip=True)
    sonrisa_social = forms.CharField(max_length=100, required=False, label="Sonrisa Social (edad)", strip=True)
    sentarse = forms.CharField(max_length=100, required=False, label="Sedestación (edad)", strip=True)
    gatear = forms.CharField(max_length=100, required=False, label="Gateo (edad)", strip=True)
    pararse = forms.CharField(max_length=100, required=False, label="Bipedestación (edad)", strip=True)
    caminar = forms.CharField(max_length=100, required=False, label="Marcha (edad)", strip=True)
    primeras_palabras = forms.CharField(max_length=100, required=False, label="Primeras Palabras (edad)", strip=True)
    primeros_dientes = forms.CharField(max_length=100, required=False, label="Primeros Dientes (edad)", strip=True)
    progreso_escuela = forms.CharField(max_length=100, required=False, label="Progreso Escolar", strip=True)
    progreso_peso = forms.CharField(max_length=100, required=False, label="Progreso Ponderal (Peso)", strip=True)
    progreso_talla = forms.CharField(max_length=100, required=False, label="Progreso Estatural (Talla)", strip=True)

    peso_nacer = forms.DecimalField(required=False, max_digits=5, decimal_places=2, label="Peso al Nacer (kg)", widget=forms.NumberInput(attrs={'step': '0.01', 'min':'0'}))
    talla_nacer = forms.DecimalField(required=False, max_digits=5, decimal_places=2, label="Talla al Nacer (cm)", widget=forms.NumberInput(attrs={'step': '0.01', 'min':'0'}))
    circunferencia_cefalica = forms.DecimalField(required=False, max_digits=5, decimal_places=2, label="Circunferencia Cefálica (cm)", widget=forms.NumberInput(attrs={'step': '0.01', 'min':'0'}))
    cianosis = forms.CharField(max_length=100, required=False, label="Cianosis Neonatal", strip=True)
    ictericia = forms.CharField(max_length=100, required=False, label="Ictericia Neonatal", strip=True)
    hemorragia = forms.CharField(max_length=100, required=False, label="Hemorragia Neonatal", strip=True)
    infecciones = forms.CharField(max_length=100, required=False, label="Infecciones Neonatales", strip=True)
    convulsiones = forms.CharField(max_length=100, required=False, label="Convulsiones Neonatales", strip=True)
    vomitos = forms.CharField(max_length=100, required=False, label="Vómitos Neonatales", strip=True)
    observacion_complicaciones = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}), label="Observaciones (Complicaciones Neonatales)", strip=True)
    otros_complicaciones = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}), label="Otras Complicaciones Neonatales", strip=True)
    tipo_alimentacion = forms.ChoiceField(
        choices=[('', '---------')] + PeriodoNeonatal._meta.get_field('tipo_alimentacion').choices,
        required=False, label="Tipo de Alimentación Inicial"
    )
    observaciones_alimentacion = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}), label="Observaciones (Alimentación)", strip=True)
    evolucion = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}), label="Evolución General Neonatal", strip=True)
    observaciones_habitos_psicologicos = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}), label="Observaciones (Hábitos Psicobiológicos)", strip=True)

    def clean_fur(self):
        fecha = self.cleaned_data.get('fur')
        if fecha and fecha > timezone.now().date():
            raise forms.ValidationError("La FUR no puede ser una fecha futura.")
        return fecha

    def clean_edad_gestacional(self):
        edad_g = self.cleaned_data.get('edad_gestacional')
        if edad_g is not None and (edad_g < 18 or edad_g > 45):
            raise forms.ValidationError("Ingrese una edad gestacional válida (ej: 18-45 semanas).")
        return edad_g

    def _clean_non_negative_integer(self, field_name):
        value = self.cleaned_data.get(field_name)
        if value is not None and value < 0:
            self.add_error(field_name, "Este valor no puede ser negativo.")
        return value

    def clean_numero_partos(self): return self._clean_non_negative_integer('numero_partos')
    def clean_numero_gestas(self): return self._clean_non_negative_integer('numero_gestas')
    def clean_numero_cesareas(self): return self._clean_non_negative_integer('numero_cesareas')
    def clean_numero_abortos(self): return self._clean_non_negative_integer('numero_abortos')
    def clean_numero_mortinatos(self): return self._clean_non_negative_integer('numero_mortinatos')
    def clean_numero_malformaciones(self): return self._clean_non_negative_integer('numero_malformaciones')

    def clean_peso_nacer(self):
        peso = self.cleaned_data.get('peso_nacer')
        if peso is not None and (peso <= 0 or peso > 10):
             raise forms.ValidationError("Ingrese un peso válido (ej: 0.1 - 10 kg).")
        return peso

    def clean_talla_nacer(self):
        talla = self.cleaned_data.get('talla_nacer')
        if talla is not None and (talla <= 20 or talla > 70):
             raise forms.ValidationError("Ingrese una talla válida (ej: 20 - 70 cm).")
        return talla

    def clean_circunferencia_cefalica(self):
        cc = self.cleaned_data.get('circunferencia_cefalica')
        if cc is not None and (cc <= 15 or cc > 50):
             raise forms.ValidationError("Ingrese una circunferencia cefálica válida (ej: 15 - 50 cm).")
        return cc

    def clean(self):
        cleaned_data = super().clean()
        exposicion = cleaned_data.get('exposicion_teratogenos')
        descripcion_exp = cleaned_data.get('descripcion_exposicion')
        if exposicion and not descripcion_exp:
            self.add_error('descripcion_exposicion', "Debe describir la exposición si seleccionó un tipo.")

        num_gestas = cleaned_data.get('numero_gestas')
        num_partos = cleaned_data.get('numero_partos')
        num_cesareas = cleaned_data.get('numero_cesareas')

        if num_partos is not None and num_gestas is not None and num_partos > num_gestas:
            self.add_error('numero_partos', "El número de partos no puede exceder el número de gestas.")
        if num_cesareas is not None and num_partos is not None and num_cesareas > num_partos:
            self.add_error('numero_cesareas', "El número de cesáreas no puede exceder el número de partos.")

        return cleaned_data

    def save(self, proposito=None, pareja=None):
        if not proposito and not pareja:
            raise ValueError("Debe proporcionar un propósito o una pareja para guardar los antecedentes.")
        if proposito and pareja:
            raise ValueError("No puede proporcionar tanto un propósito como una pareja simultáneamente.")

        ap_defaults = {
            'fur': self.cleaned_data.get('fur'),
            'edad_gestacional': self.cleaned_data.get('edad_gestacional'),
            'controles_prenatales': self.cleaned_data.get('controles_prenatales', ''),
            'numero_partos': self.cleaned_data.get('numero_partos'),
            'numero_gestas': self.cleaned_data.get('numero_gestas'),
            'numero_cesareas': self.cleaned_data.get('numero_cesareas'),
            'numero_abortos': self.cleaned_data.get('numero_abortos'),
            'numero_mortinatos': self.cleaned_data.get('numero_mortinatos'),
            'numero_malformaciones': self.cleaned_data.get('numero_malformaciones'),
            'complicaciones_embarazo': self.cleaned_data.get('complicaciones_embarazo'),
            'exposicion_teratogenos': self.cleaned_data.get('exposicion_teratogenos') or None,
            'descripcion_exposicion': self.cleaned_data.get('descripcion_exposicion'),
            'enfermedades_maternas': self.cleaned_data.get('enfermedades_maternas'),
            'complicaciones_parto': self.cleaned_data.get('complicaciones_parto'),
            'otros_antecedentes': self.cleaned_data.get('otros_antecedentes'),
            'observaciones': self.cleaned_data.get('observaciones')
        }
        ap_defaults = {k:v for k,v in ap_defaults.items() if v is not None or k=='controles_prenatales'}


        if proposito:
            antecedentes, _ = AntecedentesPersonales.objects.update_or_create(
                proposito=proposito, defaults=ap_defaults
            )
        else:
            antecedentes, _ = AntecedentesPersonales.objects.update_or_create(
                pareja=pareja, defaults=ap_defaults
            )

        dp_defaults = {
            'sostener_cabeza': self.cleaned_data.get('sostener_cabeza'),
            'sonrisa_social': self.cleaned_data.get('sonrisa_social'),
            'sentarse': self.cleaned_data.get('sentarse'),
            'gatear': self.cleaned_data.get('gatear'),
            'pararse': self.cleaned_data.get('pararse'),
            'caminar': self.cleaned_data.get('caminar'),
            'primeras_palabras': self.cleaned_data.get('primeras_palabras'),
            'primeros_dientes': self.cleaned_data.get('primeros_dientes'),
            'progreso_escuela': self.cleaned_data.get('progreso_escuela'),
            'progreso_peso': self.cleaned_data.get('progreso_peso'),
            'progreso_talla': self.cleaned_data.get('progreso_talla')
        }
        dp_defaults = {k:v for k,v in dp_defaults.items() if v is not None}


        if proposito:
            desarrollo, _ = DesarrolloPsicomotor.objects.update_or_create(
                proposito=proposito, defaults=dp_defaults
            )
        else:
            desarrollo, _ = DesarrolloPsicomotor.objects.update_or_create(
                pareja=pareja, defaults=dp_defaults
            )

        pn_defaults = {
            'peso_nacer': self.cleaned_data.get('peso_nacer'),
            'talla_nacer': self.cleaned_data.get('talla_nacer'),
            'circunferencia_cefalica': self.cleaned_data.get('circunferencia_cefalica'),
            'cianosis': self.cleaned_data.get('cianosis'),
            'ictericia': self.cleaned_data.get('ictericia'),
            'hemorragia': self.cleaned_data.get('hemorragia'),
            'infecciones': self.cleaned_data.get('infecciones'),
            'convulsiones': self.cleaned_data.get('convulsiones'),
            'vomitos': self.cleaned_data.get('vomitos'),
            'observacion_complicaciones': self.cleaned_data.get('observacion_complicaciones'),
            'otros_complicaciones': self.cleaned_data.get('otros_complicaciones'),
            'tipo_alimentacion': self.cleaned_data.get('tipo_alimentacion') or None,
            'observaciones_alimentacion': self.cleaned_data.get('observaciones_alimentacion'),
            'evolucion': self.cleaned_data.get('evolucion'),
            'observaciones_habitos_psicologicos': self.cleaned_data.get('observaciones_habitos_psicologicos')
        }
        pn_defaults = {k:v for k,v in pn_defaults.items() if v is not None}

        if proposito:
            neonatal, _ = PeriodoNeonatal.objects.update_or_create(
                proposito=proposito, defaults=pn_defaults
            )
        else:
            neonatal, _ = PeriodoNeonatal.objects.update_or_create(
                pareja=pareja, defaults=pn_defaults
            )
        return antecedentes, desarrollo, neonatal

class AntecedentesPreconcepcionalesForm(forms.Form):
    antecedentes_padre = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}), label="Antecedentes Familiares Paternos Relevantes", strip=True)
    antecedentes_madre = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}), label="Antecedentes Familiares Maternos Relevantes", strip=True)
    estado_salud_padre = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}), label="Estado de Salud Actual del Padre", strip=True)
    estado_salud_madre = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}), label="Estado de Salud Actual de la Madre", strip=True)
    fecha_union_pareja = forms.DateField(required=False, widget=DateInput(attrs={'type': 'date', 'class':'form-control'}), label="Fecha de Unión de la Pareja (si aplica)")
    consanguinidad = forms.ChoiceField(
        choices=[('', '---------'), ('Sí', 'Sí'), ('No', 'No')],
        required=False, label="Consanguinidad entre los padres"
    )
    grado_consanguinidad = forms.CharField(max_length=50, required=False, label="Grado de Consanguinidad (si aplica)", strip=True)

    def clean_fecha_union_pareja(self):
        fecha = self.cleaned_data.get('fecha_union_pareja')
        if fecha and fecha > timezone.now().date():
            raise forms.ValidationError("La fecha de unión no puede ser en el futuro.")
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        consanguinidad_val = cleaned_data.get('consanguinidad')
        grado_consanguinidad_val = cleaned_data.get('grado_consanguinidad')

        if consanguinidad_val == 'Sí' and not grado_consanguinidad_val:
            self.add_error('grado_consanguinidad', "Debe especificar el grado si existe consanguinidad.")
        elif consanguinidad_val == 'No' and grado_consanguinidad_val:
            cleaned_data['grado_consanguinidad'] = ''
        return cleaned_data

    def save(self, proposito=None, pareja=None, tipo=None):
        if tipo not in ['proposito', 'pareja']:
            raise ValueError("Tipo debe ser 'proposito' o 'pareja'")

        if tipo == 'proposito' and not proposito:
            raise ValueError("Debe proporcionar un propósito para el tipo 'proposito'")
        if tipo == 'pareja' and not pareja:
            raise ValueError("Debe proporcionar una pareja para el tipo 'pareja'")

        afp_defaults = {
            'antecedentes_padre': self.cleaned_data.get('antecedentes_padre'),
            'antecedentes_madre': self.cleaned_data.get('antecedentes_madre'),
            'estado_salud_padre': self.cleaned_data.get('estado_salud_padre'),
            'estado_salud_madre': self.cleaned_data.get('estado_salud_madre'),
            'fecha_union_pareja': self.cleaned_data.get('fecha_union_pareja'),
            'consanguinidad': self.cleaned_data.get('consanguinidad') or None,
            'grado_consanguinidad': self.cleaned_data.get('grado_consanguinidad')
        }
        if afp_defaults['consanguinidad'] != 'Sí':
            afp_defaults['grado_consanguinidad'] = ''

        afp_defaults_clean = {k:v for k,v in afp_defaults.items() if v is not None or (k == 'grado_consanguinidad' and afp_defaults['consanguinidad'] == 'Sí')}


        if tipo == 'proposito':
            antecedentespre, _ = AntecedentesFamiliaresPreconcepcionales.objects.update_or_create(
                proposito=proposito, defaults=afp_defaults_clean
            )
        else:
            antecedentespre, _ = AntecedentesFamiliaresPreconcepcionales.objects.update_or_create(
                pareja=pareja, defaults=afp_defaults_clean
            )
        return antecedentespre

class ExamenFisicoForm(ModelForm):
    class Meta:
        model = ExamenFisico
        fields = '__all__'
        exclude = ['examen_id', 'fecha_examen', 'proposito'] # Exclude examen_id too if it's AutoField
        widgets = {
            'medida_abrazada': forms.NumberInput(attrs={'step': '0.01'}),
            'segmento_inferior': forms.NumberInput(attrs={'step': '0.01'}),
            'segmento_superior': forms.NumberInput(attrs={'step': '0.01'}),
            'circunferencia_cefalica': forms.NumberInput(attrs={'step': '0.01'}),
            'talla': forms.NumberInput(attrs={'step': '0.01'}),
            'distancia_intermamilar': forms.NumberInput(attrs={'step': '0.01'}),
            'distancia_interc_interna': forms.NumberInput(attrs={'step': '0.01'}),
            'distancia_interpupilar': forms.NumberInput(attrs={'step': '0.01'}),
            'longitud_mano_derecha': forms.NumberInput(attrs={'step': '0.01'}),
            'longitud_mano_izquierda': forms.NumberInput(attrs={'step': '0.01'}),
            'peso': forms.NumberInput(attrs={'step': '0.01'}),
            'ss_si': forms.NumberInput(attrs={'step': '0.01'}),
            'distancia_interc_externa': forms.NumberInput(attrs={'step': '0.01'}),
            'ct': forms.NumberInput(attrs={'step': '0.01'}),
            'pabellones_auriculares': forms.NumberInput(attrs={'step': '0.01'}),
            'tension_arterial_sistolica': forms.NumberInput(attrs={'step': '1'}),
            'tension_arterial_diastolica': forms.NumberInput(attrs={'step': '1'}),
            'observaciones_cabeza': forms.Textarea(attrs={'rows': 1}),
            'observaciones_cuello': forms.Textarea(attrs={'rows': 1}),
            'observaciones_torax': forms.Textarea(attrs={'rows': 1}),
            'observaciones_abdomen': forms.Textarea(attrs={'rows': 1}),
            'observaciones_genitales': forms.Textarea(attrs={'rows': 1}),
            'observaciones_espalda': forms.Textarea(attrs={'rows': 1}),
            'observaciones_miembros_superiores': forms.Textarea(attrs={'rows': 1}),
            'observaciones_miembros_inferiores': forms.Textarea(attrs={'rows': 1}),
            'observaciones_piel': forms.Textarea(attrs={'rows': 1}),
            'observaciones_osteomioarticular': forms.Textarea(attrs={'rows': 1}),
            'observaciones_neurologico': forms.Textarea(attrs={'rows': 1}),
            'observaciones_pliegues': forms.Textarea(attrs={'rows': 1}),
        }

    def _clean_positive_decimal(self, field_name, max_val=None, min_val=0):
        value = self.cleaned_data.get(field_name)
        if value is not None:
            if value < min_val:
                raise forms.ValidationError(f"Este valor debe ser mayor o igual a {min_val}.")
            if max_val and value > max_val:
                raise forms.ValidationError(f"Este valor no debe exceder {max_val}.")
        return value

    def clean_medida_abrazada(self): return self._clean_positive_decimal('medida_abrazada', 300)
    def clean_segmento_inferior(self): return self._clean_positive_decimal('segmento_inferior', 200)
    def clean_segmento_superior(self): return self._clean_positive_decimal('segmento_superior', 200)
    def clean_circunferencia_cefalica(self): return self._clean_positive_decimal('circunferencia_cefalica', 100)
    def clean_talla(self): return self._clean_positive_decimal('talla', 300)
    def clean_peso(self): return self._clean_positive_decimal('peso', 500, min_val=0.1)
    def clean_tension_arterial_sistolica(self): return self._clean_positive_decimal('tension_arterial_sistolica', 300, min_val=10)
    def clean_tension_arterial_diastolica(self): return self._clean_positive_decimal('tension_arterial_diastolica', 200, min_val=10)

    def save(self, commit=True):
        examenfisico = super().save(commit=False)

        if hasattr(self, 'proposito_instance') and self.proposito_instance:
            examenfisico.proposito = self.proposito_instance
        elif not examenfisico.proposito_id and not (self.instance and self.instance.proposito_id): # check instance too
             raise ValueError("El propósito debe estar asignado para guardar el Examen Físico.")

        if commit:
            examenfisico.save()
        return examenfisico




class EvaluacionGeneticaForm(forms.ModelForm):
    class Meta:
        model = EvaluacionGenetica
        fields = ['signos_clinicos']
        widgets = {
            'signos_clinicos': forms.Textarea(attrs={
                'rows': 10,
                'class': 'form-control'
            }),
        }

class DiagnosticoPresuntivoForm(forms.ModelForm):
    class Meta:
        model = DiagnosticoPresuntivo
        fields = '__all__' # Correcto, mantenemos esto.
        widgets = {
            'descripcion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el diagnóstico presuntivo'
            }),
            'evaluacion': forms.HiddenInput(),
            # ===== NUEVA LÍNEA CRUCIAL =====
            # Le decimos a Django que el campo 'orden' existe pero no es visible.
            'orden': forms.HiddenInput(), 
        }
class PlanEstudioEditForm(forms.ModelForm):
    # --- CAMPO ELIMINADO ---
    # Ya no definimos 'archivos_nuevos' aquí.
    # Lo manejaremos directamente en el HTML y la vista.
    
    # Campo para seleccionar archivos existentes para eliminar (ESTE SE QUEDA)
    archivos_a_eliminar = forms.ModelMultipleChoiceField(
        queryset=ArchivoPlanEstudio.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Marcar archivos para eliminar"
    )

    class Meta:
        model = PlanEstudio
        fields = ['accion', 'asesoramiento_evoluciones', 'fecha_visita', 'completado']
        widgets = {
            'accion': forms.Textarea(attrs={'rows': 3}),
            'asesoramiento_evoluciones': forms.Textarea(attrs={'rows': 3}),
            'fecha_visita': forms.DateInput(attrs={'type': 'date'}),
            'completado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'accion': 'Acción a Realizar (Plan de Estudio)',
            'asesoramiento_evoluciones': 'Asesoramiento y Evoluciones (Resultados)',
            'fecha_visita': 'Fecha de Próxima Visita',
            'completado': 'Marcar como Completado',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['archivos_a_eliminar'].queryset = self.instance.archivos.all()
            self.fields['archivos_a_eliminar'].label_from_instance = lambda obj: obj.get_display_name()

    def save(self, commit=True):
        plan_estudio = super().save(commit=commit)

        if self.cleaned_data.get('archivos_a_eliminar'):
            for archivo_obj in self.cleaned_data['archivos_a_eliminar']:
                if archivo_obj.archivo:
                    if os.path.isfile(archivo_obj.archivo.path):
                        os.remove(archivo_obj.archivo.path)
                archivo_obj.delete()
                
        return plan_estudio
class PlanEstudioForm(forms.ModelForm):
    class Meta:
        model = PlanEstudio
        fields = '__all__' # Correcto, mantenemos esto.
        widgets = {
            'accion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción de la acción'
            }),
            'fecha_visita': forms.DateInput(attrs={
                'type': 'date', # Esto creará un input de fecha nativo del navegador
                'class': 'form-control'
            }),
            'completado': forms.HiddenInput(),
            
            'asesoramiento_evoluciones': forms.HiddenInput(),
            'evaluacion': forms.HiddenInput(),
        }

# Factories para los formsets
DiagnosticoFormSet = inlineformset_factory(
    EvaluacionGenetica,
    DiagnosticoPresuntivo,
    form=DiagnosticoPresuntivoForm,
    extra=1,
    can_delete=True,
    # === LÍNEAS A AÑADIR ===
    min_num=0, # Permite explícitamente que se envíen CERO formularios.
    validate_min=False # No lances un error de validación si se envían cero.
    # ========================
)

PlanEstudioFormSet = inlineformset_factory(
    EvaluacionGenetica,
    PlanEstudio,
    form=PlanEstudioForm,
    extra=1,
    can_delete=True,
    
    # === LÍNEAS A AÑADIR ===
    min_num=0, # Permite explícitamente que se envíen CERO formularios.
    validate_min=False # No lances un error de validación si se envían cero.
    # ========================
)
class PatientSearchForm(forms.Form):
    """Un formulario más simple, dedicado únicamente a la página de Gestión de Pacientes."""
    buscar_paciente = forms.CharField(
        required=False,
        label="Buscar paciente",
        widget=forms.TextInput(attrs={'placeholder': 'Nombre, apellido o ID'})
    )
    estado = forms.ChoiceField(
        choices=[], # Se poblará en la vista
        required=False,
        label="Estado",
    )
    genetista = forms.ModelChoiceField(
        queryset=Genetistas.objects.none(), 
        required=False,
        label="Genetista",
        empty_label="Todos los Genetistas"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        estado_choices = kwargs.pop('estado_choices', [])
        super().__init__(*args, **kwargs)
        
        # Poblar choices de estado pasados desde la vista
        self.fields['estado'].choices = [('', 'Todos los Estados')] + estado_choices

        # Lógica de Genetista (igual que antes)
        self.fields['genetista'].label_from_instance = lambda obj: obj.user.get_full_name() or obj.user.username
        if user and hasattr(user, 'genetistas'):
            user_gen_profile = user.genetistas
            if user_gen_profile.rol == 'ADM' or user.is_superuser:
                self.fields['genetista'].queryset = Genetistas.objects.filter(rol='GEN').select_related('user').order_by('user__last_name')
            elif user_gen_profile.rol == 'GEN':
                self.fields['genetista'].queryset = Genetistas.objects.filter(pk=user_gen_profile.pk)
                self.fields['genetista'].initial = user_gen_profile
                self.fields['genetista'].widget.attrs['disabled'] = True
            elif user_gen_profile.rol == 'LEC' and user_gen_profile.associated_genetista:
                self.fields['genetista'].queryset = Genetistas.objects.filter(pk=user_gen_profile.associated_genetista.pk)
                self.fields['genetista'].initial = user_gen_profile.associated_genetista
                self.fields['genetista'].widget.attrs['disabled'] = True
            else:
                self.fields['genetista'].widget.attrs['disabled'] = True


class ReportSearchForm(forms.Form):
    """El formulario robusto para la página de Reportes, ahora con más opciones."""
    REPORT_TYPE_CHOICES = [
        ('patients', 'Reporte de Pacientes'),
        ('histories', 'Reporte de Historias Clínicas'),
        ('consultations', 'Reporte de Consultas/Planes de Estudio'),
        ('diagnoses', 'Reporte de Diagnósticos Finales'),
    ]
    
    report_type = forms.ChoiceField(
        choices=REPORT_TYPE_CHOICES, required=True, label="Tipo de Reporte",
        widget=forms.Select(attrs={'id': 'report-type-select'})
    )
    date_range = forms.CharField(
        required=False, label="Rango de Fechas",
        widget=forms.TextInput(attrs={'id': 'date-range-flatpickr', 'placeholder': 'Seleccionar rango'})
    )
    genetista = forms.ModelChoiceField(
        queryset=Genetistas.objects.none(), required=False, label="Genetista",
        empty_label="Todos los Genetistas", widget=forms.Select(attrs={'id': 'genetista-select'})
    )

    # Filtros específicos para Reporte de Historias
    numero_historia_desde = forms.IntegerField(required=False, label="Desde N° Historia")
    numero_historia_hasta = forms.IntegerField(required=False, label="Hasta N° Historia")
    estado_historia = forms.ChoiceField(choices=[], required=False, label="Estado de Historia")

    # Filtros específicos para Reporte de Pacientes
    buscar_paciente = forms.CharField(required=False, label="Buscar por Paciente", widget=forms.TextInput(attrs={'placeholder': 'Nombre o ID'}))
    estado_paciente = forms.ChoiceField(choices=[], required=False, label="Estado de Paciente")

    # Filtros específicos para Reporte de Consultas
    estado_consulta = forms.ChoiceField(
        choices=[('', 'Todos'), ('pendientes', 'Pendientes'), ('completadas', 'Completadas')],
        required=False, label="Estado de la Consulta"
    )

    # Filtros específicos para Reporte de Diagnósticos
    buscar_diagnostico = forms.CharField(required=False, label="Buscar en Diagnóstico", widget=forms.TextInput(attrs={'placeholder': 'Término clave'}))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        
        # Lógica de permisos para Genetista (sin cambios)
        self.fields['genetista'].label_from_instance = lambda obj: obj.user.get_full_name() or obj.user.username
        if user and hasattr(user, 'genetistas'):
            profile = user.genetistas
            if profile.rol == 'ADM' or user.is_superuser:
                self.fields['genetista'].queryset = Genetistas.objects.filter(rol='GEN').select_related('user').order_by('user__last_name')
            elif profile.rol == 'GEN':
                self.fields['genetista'].queryset = Genetistas.objects.filter(pk=profile.pk)
                self.fields['genetista'].initial = profile
                self.fields['genetista'].widget.attrs['disabled'] = True
            elif profile.rol == 'LEC' and profile.associated_genetista:
                self.fields['genetista'].queryset = Genetistas.objects.filter(pk=profile.associated_genetista.pk)
                self.fields['genetista'].initial = profile.associated_genetista
                self.fields['genetista'].widget.attrs['disabled'] = True
        
        # Lógica de permisos para choices de estado
        if user and (user.is_superuser or (hasattr(user, 'genetistas') and user.genetistas.rol == 'ADM')):
            self.fields['estado_historia'].choices = [('', 'Todos')] + HistoriasClinicas.ESTADO_CHOICES
            self.fields['estado_paciente'].choices = [('', 'Todos')] + Propositos.ESTADO_CHOICES
        else:
            self.fields['estado_historia'].choices = [('', 'Todos')] + [c for c in HistoriasClinicas.ESTADO_CHOICES if c[0] != 'archivada']
            self.fields['estado_paciente'].choices = [('', 'Todos')] + [c for c in Propositos.ESTADO_CHOICES if c[0] != 'inactivo']

    def clean_date_range(self):
        date_range_str = self.cleaned_data.get('date_range')
        if not date_range_str: return None
        try:
            parts = date_range_str.split(' a ')
            if len(parts) == 2:
                fecha_desde = datetime.strptime(parts[0].strip(), '%d/%m/%Y').date()
                fecha_hasta = datetime.strptime(parts[1].strip(), '%d/%m/%Y').date()
                if fecha_desde > fecha_hasta: raise forms.ValidationError("La fecha 'desde' no puede ser posterior a 'hasta'.")
                return {'desde': fecha_desde, 'hasta': fecha_hasta}
            elif len(parts) == 1 and parts[0].strip():
                fecha = datetime.strptime(parts[0].strip(), '%d/%m/%Y').date()
                return {'desde': fecha, 'hasta': fecha}
        except (ValueError, IndexError):
            raise forms.ValidationError("Formato de fecha inválido. Use DD/MM/YYYY o DD/MM/YYYY a DD/MM/YYYY.")
        return None
    

class AdminUserCreationForm(forms.ModelForm):
    # === CAMBIO 1: Añadir el campo username explícitamente ===
    username = forms.CharField(max_length=150, required=True, label="Nombre de usuario", widget=forms.TextInput(attrs={'placeholder': 'Ej: j.perez'}))
    first_name = forms.CharField(max_length=30, required=True, label="Nombre", widget=forms.TextInput(attrs={'placeholder': 'Nombre del usuario'}))
    last_name = forms.CharField(max_length=150, required=True, label="Apellido", widget=forms.TextInput(attrs={'placeholder': 'Apellido del usuario'}))
    email = forms.EmailField(required=True, label="Email", widget=forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.com'}))
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")
    
    ROLE_CHOICES_WITH_EMPTY = [('', 'Seleccionar rol')] + list(Genetistas.ROL_CHOICES)
    rol = forms.ChoiceField(choices=ROLE_CHOICES_WITH_EMPTY, required=True, label="Rol")
    
    associated_genetista = forms.ModelChoiceField(
        queryset=Genetistas.objects.filter(rol='GEN').select_related('user'), 
        required=False, 
        label="Genetista Asociado",
        help_text="Requerido si el rol es Lector.",
        empty_label="Seleccionar genetista asociado"
    )

    class Meta:
        model = User
        # === CAMBIO 2: Añadir 'username' a los fields ===
        fields = ['username', 'first_name', 'last_name', 'email'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['associated_genetista'].label_suffix = "" 
        self.fields['associated_genetista'].label_from_instance = lambda obj: obj.user.get_full_name() or obj.user.username
    
    # === CAMBIO 3: Añadir validación para el nuevo campo username ===
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Un usuario con este nombre de usuario ya existe.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Un usuario con este email ya existe.")
        return email

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password_confirm

    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get('rol')
        associated_genetista = cleaned_data.get('associated_genetista')

        if rol == 'LEC' and not associated_genetista:
            self.add_error('associated_genetista', "Debe seleccionar un genetista asociado para el rol Lector.")
        
        if rol and rol != 'LEC' and associated_genetista:
            pass
            
        return cleaned_data

    def save(self, commit=True):
        # === CAMBIO 4: Usar el nuevo campo 'username' al crear el usuario ===
        user = User(
            username=self.cleaned_data['username'], 
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            is_active=True 
        )
        user.set_password(self.cleaned_data['password']) 
        
        if commit:
            user.save()
            gen_profile, created = Genetistas.objects.get_or_create(user=user) 
            
            gen_profile.rol = self.cleaned_data['rol']
            if gen_profile.rol == 'LEC':
                gen_profile.associated_genetista = self.cleaned_data['associated_genetista']
            else:
                gen_profile.associated_genetista = None 
            gen_profile.save()
        return user
    
class PasswordResetAdminForm(forms.Form):
    new_password = forms.CharField(
        label="Nueva Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'required': True, 'minlength': '8'}),
        help_text="Mínimo 8 caracteres."
    )
    confirm_password = forms.CharField(
        label="Confirmar Nueva Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'required': True})
    )

    def clean_confirm_password(self):
        password = self.cleaned_data.get('new_password')
        password_confirm = self.cleaned_data.get('confirm_password')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password_confirm
    
class AdminUserEditForm(forms.ModelForm):
    # Campos del modelo User
    username = forms.CharField(max_length=150, required=True, label="Nombre de usuario")
    first_name = forms.CharField(max_length=30, required=True, label="Nombre")
    last_name = forms.CharField(max_length=150, required=True, label="Apellido")
    email = forms.EmailField(required=True, label="Email")

    # Campos del modelo Genetistas (se manejan por separado)
    ROLE_CHOICES_WITH_EMPTY = [('', 'Seleccionar rol')] + list(Genetistas.ROL_CHOICES)
    rol = forms.ChoiceField(choices=ROLE_CHOICES_WITH_EMPTY, required=True, label="Rol")
    
    associated_genetista = forms.ModelChoiceField(
        queryset=Genetistas.objects.filter(rol='GEN').select_related('user'), 
        required=False, 
        label="Genetista Asociado",
        help_text="Requerido si el rol es Lector.",
        empty_label="Seleccionar genetista asociado"
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacemos que la lista de genetistas asociados sea más legible
        self.fields['associated_genetista'].label_from_instance = lambda obj: obj.user.get_full_name() or obj.user.username

        # ===== CAMBIO CRUCIAL: Añadimos los atributos aquí =====
        self.fields['rol'].widget.attrs.update({
            'class': 'form-input',
            'id': 'edit_rol'
        })
        self.fields['associated_genetista'].widget.attrs.update({
            'class': 'form-input',
            'id': 'edit_associated_genetista'
        })
        # =======================================================

        # Si el formulario se instancia con un usuario (para edición),
        # poblamos los campos 'rol' y 'associated_genetista' desde su perfil.
        if self.instance and self.instance.pk:
            try:
                genetista_profile = self.instance.genetistas
                self.fields['rol'].initial = genetista_profile.rol
                self.fields['associated_genetista'].initial = genetista_profile.associated_genetista
            except Genetistas.DoesNotExist:
                # Si por alguna razón el usuario no tiene perfil, lo dejamos en blanco
                pass

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Comprobamos si otro usuario (excluyendo el actual) ya tiene este nombre de usuario
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Un usuario con este nombre de usuario ya existe.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Comprobamos si otro usuario (excluyendo el actual) ya tiene este email
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Un usuario con este email ya existe.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get('rol')
        associated_genetista = cleaned_data.get('associated_genetista')

        # La misma validación que en el formulario de creación
        if rol == 'LEC' and not associated_genetista:
            self.add_error('associated_genetista', "Debe seleccionar un genetista asociado para el rol Lector.")
        
        return cleaned_data

    def save(self, commit=True):
        # Guardamos el objeto User (username, email, etc.)
        user = super().save(commit=False)
        
        if commit:
            user.save()
            # Ahora, actualizamos el perfil de Genetista relacionado
            gen_profile, created = Genetistas.objects.get_or_create(user=user)
            
            gen_profile.rol = self.cleaned_data['rol']
            if gen_profile.rol == 'LEC':
                gen_profile.associated_genetista = self.cleaned_data['associated_genetista']
            else:
                gen_profile.associated_genetista = None # Limpiamos si el rol no es Lector
            
            gen_profile.save()
        return user
    
class AutorizacionForm(forms.ModelForm):
    # Campo personalizado para el selector del representante
    representante_selector = forms.ModelChoiceField(
        queryset=InformacionPadres.objects.none(),
        required=False,
        label="Representante (Padre/Madre)",
        empty_label="Seleccione un representante..."
    )
    
    # ===== CAMPO AÑADIDO =====
    # Este campo oculto recibirá los datos Base64 de la firma desde el frontend (ej: signature_pad.js).
    # No es requerido porque el usuario puede guardar sin cambiar la firma.
    signature_data = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Autorizaciones
        # ===== CAMBIO: Excluimos 'archivo_autorizacion' ya que lo manejaremos en la vista =====
        # a partir del campo 'signature_data'.
        fields = ['autorizacion_examenes']
        widgets = {
            'autorizacion_examenes': forms.Select(choices=[('', 'Seleccione...'), (True, 'Sí'), (False, 'No')]),
        }

    def __init__(self, *args, **kwargs):
        proposito = kwargs.pop('proposito', None)
        super().__init__(*args, **kwargs)

        if proposito and proposito.is_minor():
            padres_qs = InformacionPadres.objects.filter(proposito=proposito).order_by('tipo')
            self.fields['representante_selector'].queryset = padres_qs
            self.fields['representante_selector'].label_from_instance = lambda obj: f"{obj.get_tipo_display()}: {obj.nombres} {obj.apellidos}"
            
            if self.instance and self.instance.representante_padre:
                self.fields['representante_selector'].initial = self.instance.representante_padre
        else:
             del self.fields['representante_selector']

    def save(self, commit=True):
        # Asignamos el valor del selector al campo real del modelo
        instance = super().save(commit=False)
        if 'representante_selector' in self.cleaned_data:
            instance.representante_padre = self.cleaned_data.get('representante_selector')
        
        # El guardado del archivo de firma se hará explícitamente en la VISTA.
        
        if commit:
            instance.save()
        return instance

class ArchivarHistoriaForm(forms.Form):
    motivo = forms.CharField(
        label="Motivo para Archivar",
        required=True,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Describa brevemente la razón por la cual se archiva esta historia clínica...',
            'class': 'form-input'
        }),
        help_text="Este motivo será registrado y visible para los administradores."
    )