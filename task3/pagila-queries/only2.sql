-- 2. Топ-10 актеров по количеству аренд
SELECT CONCAT(a.first_name, ' ', a.last_name) AS actor_name, COUNT(r.rental_id) AS total_rentals
FROM actor a
JOIN film_actor fa ON a.actor_id = fa.actor_id
JOIN film f ON fa.film_id = f.film_id
JOIN inventory i ON f.film_id = i.film_id
JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY a.actor_id, a.first_name, a.last_name
ORDER BY total_rentals DESC
LIMIT 10;