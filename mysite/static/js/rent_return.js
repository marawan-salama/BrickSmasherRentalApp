let userId = 0;

$(document).ready(() => fetchAllMovies());

const fetchAllMovies = () => {
    $.get("/dbMovie/")
        .done(data => {
            const availableMovies = data.filter(movie => movie.stock >= 1);
            $("#all-movies-table-body").html(renderMoviesTable(availableMovies));
        })
        .fail(({ responseJSON }) => {
            $("#error-message").text(responseJSON.error);
            $("#all-movies-table-body").html(renderMoviesTable([]));
        });
};

const fetchMember = () => {
    const email = $('#member-email').val().trim();
    if (email) {
        $.get("/dbUser/", { email })
            .done(data => {
                $('#member-info').html(`Member: ${data.first_name} ${data.last_name}`);
                userId = data.user_id;
                fetchCheckedOutMovies(userId);
            })
            .fail(({ responseJSON }) => handleError(responseJSON.error));
    } else {
        handleError('Please enter a valid email.');
    }
};

const fetchCheckedOutMovies = user_id => {
    $.get("/dbRent/", { user_id })
        .done(data => $("#checked-out-container").html(renderCheckedOutTable(data)))
        .fail(({ responseJSON }) => handleError(responseJSON.error));
};

const renderCheckedOutTable = movies => `
    <h2>Checked Out Movies</h2>
    <table id="checked-out-table">
        <thead>
            <tr><th>Title</th></tr>
        </thead>
        <tbody>${renderMoviesTable(movies, false)}</tbody>
    </table>
`;

const renderMoviesTable = (movies, checkOut = true) => 
    movies.map(movie => renderMovieRow(movie, checkOut)).join('');

const renderMovieRow = (movie, checkOut) => `
    <tr>
        <td class='rent-return-item' onclick="toggleMovieCheckout('${movie.movie_id}', '${checkOut ? "rent" : "return"}')">${movie.title}</td>
    </tr>
`;

const toggleMovieCheckout = (movieId, action) => {
    $.post("/dbRent/", { action, user_id: userId, movie_id: movieId })
        .done(() => {
            fetchAllMovies();
            fetchCheckedOutMovies(userId);
            $("#error-message").empty();
        })
        .fail(({ responseJSON }) => $("#error-message").text(responseJSON.error));
};

const handleError = (message) => {
    $("#error-message").text(message);
    $('#member-info').empty();
    userId = 0;
    $("#checked-out-container").empty();
};


