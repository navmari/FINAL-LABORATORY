document.addEventListener("DOMContentLoaded", () => {
    console.log("Dashboard loaded");

    // Use SweetAlert2 for confirmation modals when data-confirm present
    function showConfirm(message){
        return Swal.fire({
            title: message,
            icon: 'question',
            showCancelButton: true,
            confirmButtonText: 'Yes',
            cancelButtonText: 'Cancel'
        });
    }

    // Intercept submit for forms that have data-confirm attribute
    document.querySelectorAll('form[data-confirm]').forEach(form => {
        form.addEventListener('submit', function(ev){
            const msg = this.dataset.confirm;
            if(!msg) return; // no confirm message, proceed
            ev.preventDefault();
            showConfirm(msg).then(result => {
                if(result.isConfirmed){
                    this.submit();
                }
            });
        });
    });

    // Intercept clicks on buttons with data-confirm to show prompt and submit enclosing form
    document.querySelectorAll('button[data-confirm]').forEach(btn => {
        btn.addEventListener('click', function(ev){
            const msg = this.dataset.confirm;
            if(!msg) return; // no confirm message, proceed
            ev.preventDefault();
            ev.stopPropagation();
            const form = this.closest('form');
            showConfirm(msg).then(result => {
                if(result.isConfirmed){
                    if(form) form.submit();
                    else {
                        // fallback: if button is not in a form, try to trigger click
                        this.click();
                    }
                }
            });
        });
    });
});
