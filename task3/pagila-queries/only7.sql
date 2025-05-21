-- 7. Категория с наибольшим временем аренды для городов на "a" и с "-"
SELECT 'starts_with_a' AS city_type, c.name AS category_name, SUM(EXTRACT(EPOCH FROM (r.return_date - r.rental_date)) / 3600.0) AS total_hours
FROM category c
JOIN film_category fc ON c.category_id = fc.category_id
JOIN film f ON fc.film_id = f.film_id
JOIN inventory i ON f.film_id = i.film_id
JOIN rental r ON i.inventory_id = r.inventory_id
JOIN customer cu ON r.customer_id = cu.customer_id
JOIN address ad ON cu.address_id = ad.address_id
JOIN city ci ON ad.city_id = ci.city_id
WHERE ci.city ILIKE 'a%'
AND r.return_date IS NOT NULL
AND r.rental_date IS NOT NULL
GROUP BY c.category_id, c.name

UNION ALL

SELECT 'contains_hyphen' AS city_type, c.name AS category_name, SUM(EXTRACT(EPOCH FROM (r.return_date - r.rental_date)) / 3600.0) AS total_hours
FROM category c
JOIN film_category fc ON c.category_id = fc.category_id
JOIN film f ON fc.film_id = f.film_id
JOIN inventory i ON f.film_id = i.film_id
JOIN rental r ON i.inventory_id = r.inventory_id
JOIN customer cu ON r.customer_id = cu.customer_id
JOIN address ad ON cu.address_id = ad.address_id
JOIN city ci ON ad.city_id = ci.city_id
WHERE ci.city ILIKE '%-%'
AND r.return_date IS NOT NULL
AND r.rental_date IS NOT NULL
GROUP BY c.category_id, c.name;