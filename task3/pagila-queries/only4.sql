-- 4. Фильмы, которых нет в инвентаре, без использования IN
SELECT f.title
FROM film f
LEFT JOIN inventory i ON f.film_id = i.film_id
WHERE i.inventory_id IS NULL;