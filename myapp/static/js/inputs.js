
document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('diagnosticos-container');
    const addButton = document.getElementById('add-diagnostico');
    const totalForms = document.getElementById('id_diagnosticos-TOTAL_FORMS');
    const formPrefix = 'diagnosticos';
    
    addButton.addEventListener('click', function() {
        const formCount = parseInt(totalForms.value);
        const newForm = document.createElement('div');
        newForm.className = 'diagnostico-item form-row';
        newForm.innerHTML = `
            <input type="hidden" name="${formPrefix}-${formCount}-id" id="id_${formPrefix}-${formCount}-id">
            <div class="flex-grow-1">
                <input type="text" name="${formPrefix}-${formCount}-descripcion" 
                       class="form-control" placeholder="Ingrese diagnóstico presuntivo" 
                       id="id_${formPrefix}-${formCount}-descripcion">
            </div>
            <div class="ml-2">
                <input type="checkbox" name="${formPrefix}-${formCount}-DELETE" 
                       id="id_${formPrefix}-${formCount}-DELETE">
                <label>Eliminar</label>
            </div>
        `;
        container.appendChild(newForm);
        totalForms.value = formCount + 1;
    });
});
