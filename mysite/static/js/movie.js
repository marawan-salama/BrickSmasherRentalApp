const addMovie = () => {
    const title = $("#new-movie-title").val().trim();
    $.post("/dbMovie/", { action: "new", title })
        .done(() => {
            fetchAllMovies();
            $("#error-message").empty();
        })
        .fail(({ responseJSON }) => $("#error-message").text(responseJSON.error));
}

const updateMovieStock = (movieId, action) => {
    $.post("/dbMovie/", { movie_id: movieId, action })
        .done(() => {
            fetchAllMovies();
            $("#error-message").empty();
        })
        .fail(({ responseJSON }) => $("#error-message").text(responseJSON.error));
}

const renderMoviesTable = movies => movies.map(renderMovieRow).join('');

const renderMovieRow = ({ movie_id, title, stock, checked_out }) => `
    <tr id='movie-${movie_id}'>
        <td>${title}</td>
        <td class='stock'>${stock}</td>
        <td class='checkedOut'>${checked_out}</td>
        <td>
            <button class='act-btn' onclick='updateMovieStock(${movie_id}, "add")'>+</button>
            <button class='act-btn' onclick='updateMovieStock(${movie_id}, "remove")'>-</button>
        </td>
    </tr>
`;

const fetchAllMovies = () => {
    $.get("/dbMovie/")
        .done(data => $("#movies-table-body").html(renderMoviesTable(data)))
        .fail(({ responseJSON }) => {
            $("#error-message").text(responseJSON.error);
            $("#movies-table-body").html(renderMoviesTable([]));
        });
}

$(document).ready(() => fetchAllMovies());
