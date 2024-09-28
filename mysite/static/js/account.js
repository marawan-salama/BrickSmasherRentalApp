const createAccount = () => {
    // Using destructuring and template literals for cleaner code
    const [first_name, last_name, email] = ['#first-name', '#last-name', '#email'].map(
        selector => $(selector).val().trim()
    );

    // Using object shorthand notation in AJAX request
    $.post("/dbUser/", { first_name, last_name, email })
        .done(({ first_name, last_name }) => {
            // Using template literals to format the success message
            $("#success-message").text(`Account created successfully for ${first_name} ${last_name}`);
            $("#error-message").empty();  // Clear any existing error message
        })
        .fail(({ responseJSON }) => {
            // Accessing error directly
            $("#error-message").text(responseJSON.error);
            $("#success-message").empty();  // Clear any existing success message
        });
}
