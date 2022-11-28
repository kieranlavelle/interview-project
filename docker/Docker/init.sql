CREATE TABLE "service_providers" (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  "name" text NOT NULL,
  "user_id" uuid NOT NULL,
  "cost_in_pence" integer NOT NULL,
  "review_rating" integer NOT NULL
);

CREATE TABLE "service_provider_skills" (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  "service_provider_id" uuid NOT NULL,
  "skill" text NOT NULL,
   CONSTRAINT fk_service_provider
      FOREIGN KEY(service_provider_id) 
	  REFERENCES service_providers(id)
);

CREATE TABLE "service_provider_availability" (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  "service_provider_id" uuid NOT NULL,
  "availability" daterange NOT NULL,
   CONSTRAINT fk_service_provider
      FOREIGN KEY(service_provider_id) 
	  REFERENCES service_providers(id)
);