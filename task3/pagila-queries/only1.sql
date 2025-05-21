-- 1. Количество фильмов в каждой категории, отсортированных по убыванию
SELECT c.name AS category_name, COUNT(fc.film_id) AS number_of_films
FROM category c
JOIN film_category fc ON c.category_id = fc.category_id
GROUP BY c.category_id, c.name
ORDER BY number_of_films DESC;