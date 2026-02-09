-- Drop existing tables if they exist
DROP TABLE IF EXISTS venues CASCADE;
DROP TABLE IF EXISTS venue_types CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS events_discarded CASCADE;
DROP VIEW IF EXISTS events_combined;
DROP TABLE IF EXISTS e_tags CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS themes CASCADE;
DROP TABLE IF EXISTS genres CASCADE;

-- Create table venue_types
CREATE TABLE venue_types (
    id SERIAL PRIMARY KEY,
    external_id SERIAL,
    type VARCHAR NOT NULL
);

-- Populate venue_types
INSERT INTO venue_types (type) VALUES
('Opera house'),
('Concert hall'),
('Night club'),
('Event space'),
('Open air'),
('Arena'),
('Church'),
('Theatre'),
('Boat'),
('Restaurant')
;

-- Create table venues
CREATE TABLE venues (
    id SERIAL PRIMARY KEY,
    external_id SERIAL, -- Id that may be exposed to external parties
    name VARCHAR NOT NULL,
    search_name VARCHAR,
    --type INTEGER REFERENCES venue_types(id) NOT NULL,
    address VARCHAR,
    zipcode INTEGER NOT NULL,
    city VARCHAR NOT NULL,
    country_code VARCHAR NOT NULL default 'SE',
    geo JSONB,  --not in use for now
    type VARCHAR NOT NULL, -- should later be fk venue_types.id
    default_organizer VARCHAR
);

-- Create table events
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    external_id SERIAL, -- Id that may be exposed to external parties
    data JSONB NOT NULL,
    venue_id INTEGER REFERENCES venues(id),
    source VARCHAR NOT NULL
);

CREATE UNIQUE INDEX unique_source_event_id ON events ((data->'source_data'->>'event_id'), source);


-- Create table events_discarded
CREATE TABLE events_discarded (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    source VARCHAR NOT NULL
);

-- Create view combining events and events_discarded
CREATE VIEW events_combined AS
SELECT id, data, source
FROM events
UNION ALL
SELECT id, data, source
FROM events_discarded;

-- Create table e_tags
CREATE TABLE e_tags (
    id SERIAL PRIMARY KEY,
    source VARCHAR NOT NULL,
    event_id INTEGER REFERENCES events(id),
    e_tag VARCHAR NOT NULL
);

-- Create table event_categories
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    external_id SERIAL, -- Id that may be exposed to external parties
    name VARCHAR NOT NULL,
    definition VARCHAR,
    include boolean NOT NULL default false
);

-- Populate event_categories
INSERT INTO categories (name, definition, include) VALUES
('Concert', null, true),
('Musical theatre', null, true),
('Theatre', null, true),
('Show', null, true),
('Standup', null, true),
('Dance performance', null, true),
('Full opera performance', null, true),
('Club', null, true),
('Film', 'Film & Cinema: This category includes events centered around the public viewing of films, movies, or other cinematic content. It covers screenings at cinemas, outdoor movie nights, film festivals, and other organized public film viewings. It excludes private screenings and events where film is not the main attraction.', true),
('Quiz & games', 'Quiz & Games: This category includes events where the primary activity is participating in a structured game, such as a quiz, pub quiz, bingo, or murder mystery. It excludes sports competitions and physical activities like team sports, races, or tournaments. Competitive elements within quizzes and games are still included.', true),
('Conversation', 'This category refers to staged events focused on spoken word, ideas, or literary expression. This includes poetry readings, author talks, panel discussions, debates, conversations about current news events, and other literary events. It excludes lectures, keynotes, and similar presentations primarily intended for instruction. ', true),
-- categories we want to null, filter out:
('Ghost walk', null, false),
('Spiritualist sessions', null, false),
('Exhibition', null, false),
('Flea market', null, false),
('Reincarnation therapist', null, false),
('Train ride without entertainment', null, false),
('Buss ride without entertainment', null, false),
('Boat ride without entertainment', null, false),
('Guided tour', null, false),
('City walk', null, false),
('Retreat and wellness', null, false),
('Yoga', null, false),
('Wine event', null, false),
('Beer event', null, false),
('Gift card', null, false),
('Lecture', null, false),
('Courses', null, false),
('Summer camp', null, false),
('Sport event', null, false),
('Horse event', null, false),
('Swimming', null, false),
('Football', null, false),
('Hockey', null, false),
('Sauna', null, false),
('Fair', null, false),
('LAN party', null, false),
('Club meeting', null, false),
('Membership', null, false),
('Food event', null, false),
('Champagne event', null, false),
('Poetry reading', null, false),
('Literary event', null, false),
('Running event', null, false),
('Motor sports', null, false),
('Charity event', null, false),
('Museum entrance', null, false),
('Shopping event', null, false),
('Season ticket', null, false),
('Political event', null, false),
('Crafts event', null, false),
('Workshop', null, false),
('Religious event', null, false),
('Rehearsal', null, false),
('Choir rehearsal', null, false),
('Orchestra rehearsal', null, false),
('Hotel room', null, false),
('Wardrobe fee', null, false),
('Route departure', null, false),
('Scheduled departure', null, false),
('Trotting event', null, false),
('Bootcamp', null, false),
('MMA event', null, false);

CREATE TABLE themes (
    id SERIAL PRIMARY KEY,
    external_id SERIAL, -- Id that may be exposed to external parties
    name VARCHAR NOT NULL,
    description VARCHAR
);

INSERT INTO themes (name, description) VALUES
('Explicitly Comedy', 'This theme applies only to events where the primary purpose is to make the audience laugh, featuring comedians, comedy troupes, or improv groups. Examples include stand-up shows, improv nights, and shows with a comedy focus. Excludes events with incidental humor or without a clear comedic focus.'),
('Explicitly for children and families', 'Events specifically designed for small children and their families. Exclude general all-ages events or those aimed at older children, teens or adults.'),
('Explicitly Christmas', 'This theme is for events explicitly centered on Christmas, such as Christmas music or christmas-themed performances. Excludes events with general winter themes or without clear Christmas content.'),
('Multi-day event or multi-stage event', NULL),
('Traditional circus arts', 'This theme includes events focused on circus performances, traditional or modern, such as acrobatics, juggling, clowning, and aerial acts. Excludes events where circus elements are only a minor feature.')
;
DELETE FROM themes
WHERE name='Multi-day event or multi-stage event';


CREATE TABLE genres (
    id SERIAL PRIMARY KEY,
    external_id SERIAL, -- Id that may be exposed to external parties
    name VARCHAR NOT NULL
);

INSERT INTO genres (name) VALUES
('Pop'),
('Rock'),
('Electronic'),
('Blues'),
('Jazz'),
('Country'),
('Folk'),
('Afrobeat'),
('Hip-hop'),
('R&B'),
('Reggae'),
('Hard rock'),
('Metal'),
('Dance-band'),
('Classical'),
('Soul'),
('Vocal'),
('Punk'),
('World music'),
('Gospel')
;

-- Add necessary comments for clarity
COMMENT ON VIEW events_combined IS 'View combining events and events_discarded tables';

-- Print success message
DO $$ BEGIN
    RAISE NOTICE 'Tables and view have been successfully created and populated.';
END $$;
