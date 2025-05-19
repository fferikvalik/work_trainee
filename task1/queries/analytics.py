class Analytics:
    def __init__(self, db):
        self.db = db

    def rooms_counts(self):
        return self.db.execute(
            "SELECT r.id, r.name, COUNT(s.id) AS student_count "
            "FROM rooms r LEFT JOIN students s ON s.room_id=r.id "
            "GROUP BY r.id, r.name;",
            fetch=True
        )

    def lowest_avg_age(self):
        return self.db.execute(
            "SELECT r.id, r.name, AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, s.birth_date))) AS avg_age "
            "FROM rooms r JOIN students s ON s.room_id=r.id "
            "GROUP BY r.id, r.name ORDER BY avg_age ASC LIMIT 5;",
            fetch=True
        )

    def max_age_diff(self):
        return self.db.execute(
            "SELECT r.id, r.name, "
            "(MAX(s.birth_date) - MIN(s.birth_date)) AS age_diff_days "
            "FROM rooms r JOIN students s ON s.room_id=r.id "
            "GROUP BY r.id, r.name ORDER BY age_diff_days DESC LIMIT 5;",
            fetch=True
        )

    def mixed_gender(self):
        return self.db.execute(
            "SELECT r.id, r.name FROM rooms r JOIN students s ON s.room_id=r.id "
            "GROUP BY r.id, r.name HAVING COUNT(DISTINCT s.gender)>1;",
            fetch=True
        )