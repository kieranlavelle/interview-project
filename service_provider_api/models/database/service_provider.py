INSERT_SERVICE_PROVIDER = """INSERT INTO service_providers (id, user_id, name, cost_in_pence, review_rating) VALUES (%(id)s, %(user_id)s, %(name)s, %(cost_in_pence)s, %(review_rating)s);"""
INSERT_SERVICE_PROVIDER_SKILL = """INSERT INTO service_provider_skills (service_provider_id, skill) VALUES (%(service_provider_id)s, %(skill)s);"""
INSERT_SERVICE_PROVIDER_AVAILABILITY = """INSERT INTO service_provider_availability (service_provider_id, availability) VALUES (%(service_provider_id)s, %(availability)s);"""

DELETE_SERVICE_PROVIDER = """DELETE FROM service_providers WHERE id = %(id)s AND user_id = %(user_id)s CASCADE;"""

SELECT_SERVICE_PROVIDER = """
SELECT
	sp.id,
    sp.user_id,
	sp.name,
	sp.cost_in_pence,
    sp.review_rating,
	ARRAY(
        SELECT
            skill 
        FROM 
            service_provider_skills sps
        WHERE sps.service_provider_id = sp.id
    ) AS skills,
	ARRAY(
        SELECT
            availability
        FROM 
            service_provider_availability spa
        WHERE spa.service_provider_id = sp.id
    ) AS availability 
FROM
	service_providers sp
WHERE
    sp.id = %(id)s
AND
    sp.user_id = %(user_id)s;
"""
