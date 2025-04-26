// Product Catalog JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Price range slider
    const priceRange = document.getElementById('priceRange');
    const priceValue = document.getElementById('priceValue');
    
    if (priceRange && priceValue) {
        priceRange.addEventListener('input', function() {
            priceValue.textContent = '$' + this.value;
        });
    }
    
    // Flash sale filter
    const flashCheckbox = document.getElementById('flash');
    const allCheckbox = document.getElementById('all');
    
    if (flashCheckbox && allCheckbox) {
        flashCheckbox.addEventListener('change', function() {
            if (this.checked) {
                allCheckbox.checked = false;
                filterProducts('flash');
            } else if (!allCheckbox.checked) {
                allCheckbox.checked = true;
                filterProducts('all');
            }
        });
        
        allCheckbox.addEventListener('change', function() {
            if (this.checked) {
                flashCheckbox.checked = false;
                filterProducts('all');
            } else if (!flashCheckbox.checked) {
                flashCheckbox.checked = true;
                filterProducts('flash');
            }
        });
    }
    
    // Function to filter products (would need backend integration for full functionality)
    function filterProducts(filter) {
        console.log('Filtering products by: ' + filter);
        // This would typically make an AJAX call to the server
        // or filter the products on the client side
    }
});