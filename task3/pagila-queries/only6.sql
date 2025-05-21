-- 6. Города с количеством активных и неактивных клиентов
SELECT ci.city AS city_name,
       SUM(CASE WHEN cu.active = 1 THEN 1 ELSE 0 END) AS active_customers,
       SUM(CASE WHEN cu.active = 0 THEN 1 ELSE 0 END) AS inactive_customers
FROM city ci
JOIN address ad ON ci.city_id = ad.city_id
JOIN customer cu ON ad.address_id = cu.address_id
GROUP BY ci.city_id, ci.city
ORDER BY inactive_customers DESC;
