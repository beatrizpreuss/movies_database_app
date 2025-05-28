
import statistics
from random import choice
from operator import itemgetter
from matplotlib import pyplot
from movie_storage import movie_storage_sql as storage
import requests
import os
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv('API_KEY')
MOVIE_URL = f'http://www.omdbapi.com/?apikey={API_KEY}&t='


def menu_and_input():
    """Prints menu for action selection and returns action choice as input(int)"""
    print("\n********** My Movies Database **********\n"
                            "\n"
                            "Menu:\n"
                            "0. Exit\n"
                            "1. List movies\n"
                            "2. Add movie\n"
                            "3. Delete movie\n"
                            "4. Update movie\n"
                            "5. Stats\n"
                            "6. Random movie\n"
                            "7. Search movie\n"
                            "8. Sort movies\n"
                            "9. Create rating histogram\n"
                            "10. Filter movies\n"
                            "11. Generate website")

    while True:
        try:
            user_input = int(input("\nEnter choice (0-11): "))
            return user_input
        except ValueError:
            print("\n-- Invalid input, please enter a number between 0 and 10")


def list_movies():
    """Retrieve and display all movies from the database"""
    movies = storage.list_movies()
    print(f"\n--- {len(movies)} movies in total ---")

    for movie, info in movies.items():
        print(f"{movie} ({info['year']}): {info['rating']}")


def add_movie():
    """Adds new movie and info to database based on API info fetched"""
    movies = storage.list_movies()
    movie_input = (input("\nEnter new movie name: ")).title()

    if movie_input == "" or movie_input.isspace():
        print("\n-- Invalid input, please enter a name")
        return

    elif movie_input in movies.keys():
        print("\n-- Movie already exists")
        return

    try:
        res = requests.get(f'{MOVIE_URL}{movie_input}')
        movies_resp = res.json()
    except requests.exceptions.ConnectionError:
        print("\nPlease check your connection")
        return

    try:
        title = movies_resp['Title']
        year = movies_resp['Year']
        rating_str = movies_resp['Ratings'][0]['Value']
        rating = float(rating_str.split("/")[0])
        poster = movies_resp['Poster']
        storage.add_movie(title, year, rating, poster)
    except (KeyError, ValueError):
        print("\nInvalid input or movie not found")


def delete_movie():
    """Asks user which movie to delete (name) and deletes it from database"""
    movies = storage.list_movies()
    movie_to_delete = (input("\nEnter movie name to delete: ")).title()

    if movie_to_delete not in movies.keys():
        print(f"Movie {movie_to_delete} doesn't exist!")

    else:
        del movies[movie_to_delete]
        storage.delete_movie(movie_to_delete)


def update_movie():
    """Updates movie rating based on user input"""
    movies = storage.list_movies()
    movie_to_update = (input("\nEnter movie name: ")).title()

    if movie_to_update not in movies.keys():
        print(f"Movie {movie_to_update} doesn't exist!")

    else:
        note = input("Enter movie note: ")
        movies[movie_to_update]["note"] = note

        storage.update_movie(movie_to_update, note)


def stats():
    """Calculates the average and median of all movie ratings in the database,
    and prints the best and worst movies based on ratings"""
    movies = storage.list_movies()
    ratings = []

    for info in movies.values():
        ratings.append(info["rating"])

    average = round(statistics.mean(ratings), 1)
    median = round(statistics.median(ratings), 1)
    best_movie_key, best_movie_value = max(movies.items(), key=lambda item: itemgetter('rating') (item[1]))
    worst_movie_key, worst_movie_value = min(movies.items(), key=lambda item: itemgetter('rating') (item[1]))
    print(f"\nAverage rating: {average}\n"
          f"Median rating: {median}\n"
          f"Best movie: {best_movie_key} ({best_movie_value['year']}), {best_movie_value['rating']}\n"
          f"Worst movie: {worst_movie_key} ({worst_movie_value['year']}), {worst_movie_value['rating']}")


def random_movie():
    """Prints a random movie (with info)"""
    movies = storage.list_movies()

    random_movie, info = choice(list(movies.items()))
    print(f"\n{random_movie} ({info['year']}): {info['rating']}")


def search_movie():
    """User can search for a movie based on part of its name"""
    movies = storage.list_movies()
    movie_to_search = input("\nEnter part of movie name: ")

    for key, value in movies.items():
        if movie_to_search.lower() in key.lower():
            print(f"{key} ({value['year']}): {value['rating']}")


def sorted_movies():
    """Prints the list of movies in the database ranked by rating (highest
    first) or by year (option to see latest first)"""
    movies = storage.list_movies()
    what_to_sort = (input("\nWould you like to sort by rating or by year? (r/y): ")).lower()

    if what_to_sort == "y" or what_to_sort == "year":
        order_to_sort = (input("\nDo you want to see the latest movies first? (y/n): ")).lower()
        if order_to_sort == "y" or order_to_sort == "yes":
            sorted_dict = dict(sorted(movies.items(),key=lambda item: itemgetter('year')(item[1]), reverse=True))
            print()
            for movie, info in sorted_dict.items():
                print(f"{movie} ({info['year']}): {info['rating']}")
        elif order_to_sort == "n" or order_to_sort == "no":
            sorted_dict = dict(sorted(movies.items(), key=lambda item: itemgetter('year')(item[1]), reverse=False))
            print()
            for movie, info in sorted_dict.items():
                print(f"{movie} ({info['year']}): {info['rating']}")
        else:
            print("\n-- Invalid input")

    elif what_to_sort == "r" or what_to_sort == "rating":
        sorted_dict = dict(sorted(movies.items(), key=lambda item: itemgetter('rating')(item[1]), reverse = True))
        for movie, info in sorted_dict.items():
            print(f"{movie} ({info['year']}): {info['rating']}")

    else:
        print("\n-- Invalid input")


def histogram():
    """Creates a .png file with a histogram of movie ratings"""
    movies = storage.list_movies()
    file_path = input("\nChoose file path to save histogram: ")
    values_for_histogram = []

    for info in movies.values():
        values_for_histogram.append(info["rating"])

    pyplot.hist(values_for_histogram)
    pyplot.xlabel('Ratings')
    pyplot.ylabel('Movies')
    pyplot.savefig(file_path)


def filter_movies():
    """Filters movies based on ratings and/or year"""
    movies = storage.list_movies()

    try:
        minimum_rating = input("\nEnter minimum rating (leave blank for no minimum rating): ")
        if minimum_rating == "":
            minimum_rating = 0
        else:
            minimum_rating = float(minimum_rating)

        start_year = input("Enter start year (leave blank for no start year): ")
        if start_year == "":
            start_year = 0
        else:
            start_year = int(start_year)

        end_year = input("Enter end year (leave blank for no end year): ")
        if end_year == "":
            end_year = 5000
        else:
            end_year = int(end_year)

        print(f"\n-----Filtered Movies-----\n")
        for movie, info in movies.items():
            if info['rating'] >= minimum_rating and start_year <= info['year'] <= end_year:
                print(f"{movie} ({info['year']}): {info['rating']}")

    except ValueError:
        print("\n-- Invalid input")


def generate_website():
    """ Creates website from database info """
    my_movies = ""
    movie_info = storage.get_movies_for_website()
    for title, info in movie_info.items():
        my_movies += (f'<li>'
                        f'<div class="movie">'
                        f'<img class="movie-poster" src={info['poster']} alt="Movie Poster" title="{info['note']}"/>'
                        f'<div class="movie-title">{title}</div>'
                        f'<div class="movie-year">{info["year"]}</div>'
                        f'<div class="movie-year">{info["rating"]}</div>'
                        f"</div>"
                        f"</li>")
    html = open('_static/index_template.html')
    original_html = html.read()
    replace = original_html.replace("__TEMPLATE_MOVIE_GRID__", my_movies)
    with open("_static/index.html", "w") as new_html:
        new_html.write(replace)
    print("Website was generated successfully")


def main():
    # Dictionary to store the functions and its code numbers
    actions = {
        1: list_movies,
        2: add_movie,
        3: delete_movie,
        4: update_movie,
        5: stats,
        6: random_movie,
        7: search_movie,
        8: sorted_movies,
        9: histogram,
        10: filter_movies,
        11: generate_website
    }

    user_input = -1
    while user_input <= 11:
        user_input = menu_and_input()
        if user_input == 0:
            print("Bye!")
            break
        if user_input in actions:
            actions[user_input]()
            input("\nPress enter to continue")
        else:
            print("\n-- Invalid choice, please enter a number between 0 and 10")


if __name__ == "__main__":
    main()
