$(document).ready(function() {
    var brandSelect = $('#brand-select');
    var autocompleteInput = $('#autocomplete-brand');
    var availableBrands = [
        "Honda", "Cadillac", "Toyota", "Mazda", "Chevrolet", "MINI", "Mercedes-Benz",
        "Jeep", "Maserati", "Lexus", "Audi", "Porsche", "Land", "Mitsubishi",
        "Kia", "Hyundai", "Volvo", "Volkswagen", "Ford", "FIAT", "Alfa",
        "BMW", "Nissan", "Jaguar", "Suzuki"
    ]; // Replace with your list of brand names

    autocompleteInput.on('input', function() {
        var query = autocompleteInput.val();
        var matchingBrands = availableBrands.filter(function(brand) {
            return brand.toLowerCase().includes(query.toLowerCase());
        });

        brandSelect.empty();
        brandSelect.append(new Option("Select a brand", ""));

        matchingBrands.forEach(function(brand) {
            brandSelect.append(new Option(brand, brand));
        });
    });
});
