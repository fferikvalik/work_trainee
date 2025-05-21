-- 5. Топ-3 актеров в категории Children, с учетом равных показателей
WITH actor_films AS (
    SELECT a.actor_id, a.first_name, a.last_name, COUNT(DISTINCT fa.film_id) AS film_count
    FROM actor a
    JOIN film_actor fa ON a.actor_id = fa.actor_id
    JOIN film f ON fa.film_id = f.film_id
    JOIN film_category fc ON f.film_id = fc.film_id
    JOIN category c ON fc.category_id = c.category_id
    WHERE c.name = 'Children'
    GROUP BY a.actor_id, a.first_name, a.last_name
),
top3_min AS (
    SELECT MIN(film_count) AS min_film_count
    FROM (SELECT film_count FROM actor_films ORDER BY film_count DESC LIMIT 3) AS top3
)
SELECT af.first_name, af.last_name, af.film_count
FROM actor_films af
JOIN top3_min t ON af.film_count >= t.min_film_count
ORDER BY af.film_count DESC;