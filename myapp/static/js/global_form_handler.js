/**
 * global_form_handler.js
 * Proporciona una función AJAX reutilizable y mejorada para manejar envíos de formularios.
 * 
 * Características:
 * - Envío de formularios a través de AJAX (Fetch API).
 * - Manejo de respuestas JSON (éxito con redirección o fallo con errores).
 * - Limpieza automática de errores previos en cada envío.
 * - Muestra de errores de campo y no-campo.
 * - Añade una clase 'is-invalid' a los campos con errores.
 * - Scroll automático al primer error encontrado en el formulario para mejorar la UX.
 */
function setupEnhancedAjaxForm(formId) {
    const form = document.getElementById(formId);
    if (!form) {
        console.error(`Form with ID "${formId}" not found.`);
        return;
    }

    let clickedButton = null;

    // 1. Captura qué botón de envío fue clickeado
    form.querySelectorAll('button[type="submit"]').forEach(button => {
        button.addEventListener('click', function() {
            clickedButton = this;
        });
    });

    form.addEventListener('submit', function(e) {
        e.preventDefault(); // Detener el envío normal

        const formData = new FormData(form);

        // 2. Añade el nombre y valor del botón clickeado al FormData
        if (clickedButton) {
            formData.append(clickedButton.name, clickedButton.value || '');
        }

        // --- INICIO DE LA LÓGICA DE LIMPIEZA MEJORADA ---
        // Limpiar errores de texto previos
        form.querySelectorAll('.field-errors, .non-field-errors, .error-list').forEach(el => el.innerHTML = '');
        // Quitar la clase de error de todos los inputs, selects y textareas dentro del form
        form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        const nonFieldErrorsContainer = form.querySelector('.non-field-errors');
        if (nonFieldErrorsContainer) nonFieldErrorsContainer.style.display = 'none';
        // --- FIN DE LA LÓGICA DE LIMPIEZA MEJORADA ---

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.redirect_url) {
                // Redirección exitosa
                window.location.href = data.redirect_url;
            } else if (data.errors) {
                // Manejar errores de validación
                const nonFieldErrors = form.querySelector('.non-field-errors');
                
                // Errores globales del formulario (__all__)
                if (data.errors.__all__) {
                    if (nonFieldErrors) {
                        let errorHtml = '';
                        data.errors.__all__.forEach(error => {
                            errorHtml += `<span>${error}</span>`;
                        });
                        nonFieldErrors.innerHTML = errorHtml;
                        nonFieldErrors.style.display = 'block';
                    }
                }
                
                // Errores específicos de cada campo
                for (const fieldName in data.errors) {
                    if (fieldName !== '__all__') {
                        const fieldErrorContainer = form.querySelector(`#error_id_${fieldName}`);
                        const fieldElement = document.getElementById(`id_${fieldName}`);
                        
                        if (fieldErrorContainer) {
                            let errorHtml = '';
                            data.errors[fieldName].forEach(error => {
                                errorHtml += `<span>${error.message || error}</span>`;
                            });
                            fieldErrorContainer.innerHTML = errorHtml;
                        }

                        // Añadir clase de error al input/select/textarea
                        if (fieldElement) {
                            fieldElement.classList.add('is-invalid');
                        }
                    }
                }

                // --- INICIO DE LA LÓGICA DE SCROLL AUTOMÁTICO ---
                const firstErrorElement = form.querySelector('.is-invalid, .non-field-errors:not(:empty)');
                if (firstErrorElement) {
                    firstErrorElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                }
                // --- FIN DE LA LÓGICA DE SCROLL AUTOMÁTICO ---

            } else {
                 const nonFieldErrors = form.querySelector('.non-field-errors');
                 if(nonFieldErrors) {
                    nonFieldErrors.innerHTML = '<span>Ocurrió un error inesperado. Por favor, intente de nuevo.</span>';
                    nonFieldErrors.style.display = 'block';
                 }
            }
        })
        .catch(error => {
            console.error('Error en la petición AJAX:', error);
            const nonFieldErrors = form.querySelector('.non-field-errors');
            if(nonFieldErrors) {
                nonFieldErrors.innerHTML = '<span>Error de conexión. Verifique su red e intente de nuevo.</span>';
                nonFieldErrors.style.display = 'block';
            }
        })
        .finally(() => {
            // Resetear el botón clickeado para el próximo envío
            clickedButton = null;
        });
    });
}