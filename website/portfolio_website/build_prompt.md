# JobbPulse Local Project Portfolio Build Prompt

You are a senior product architect, UX designer and full-stack engineer responsible for designing and building the public-facing JobbPulse local project portfolio.

The product has previously been referred to as a contractor directory, but it should not be designed like a traditional directory.

A traditional directory begins with a list of companies.

JobbPulse begins with real completed projects.

The primary content object is the completed project. Contractors, service categories and locations are organized around those projects.

The platform should feel like a living local portfolio of completed home-service work rather than a business listing database.

## Product Purpose

JobbPulse helps homeowners discover local contractors by browsing real work completed in their area.

Each contractor uses the JobbPulse Contractor App to document completed jobs using:

* Before photos
* After photos
* A short voice summary
* Service category
* Project location
* Additional project details

JobbPulse turns that information into a public project page.

As contractors complete more work, their portfolios grow automatically.

The combined projects from all contractors form the larger JobbPulse local project network.

The platform must communicate:

* What work was completed
* What the result looks like
* Where the work was performed
* Which contractor performed it
* How the homeowner can request similar work

Do not design the site primarily around company listings.

Design it around completed projects and visual proof.

---

# Core Product Model

The structural hierarchy should be:

1. Project
2. Contractor
3. Service
4. Location

The project is the primary discovery object.

A homeowner should be able to enter the platform through any of the following:

* A project page
* A contractor portfolio
* A service page
* A city page
* A service-and-city page
* The main project gallery

Every route should eventually lead the homeowner toward viewing relevant work and contacting the contractor who completed it.

---

# Required Public Pages

## 1. Main Homepage and Project Gallery

The homepage should immediately display real completed projects.

The primary visual element should be a large, browsable project gallery.

Each project card should contain:

* Primary project image
* Before-and-after indicator when applicable
* Project title
* Service category
* City or general service area
* Contractor name
* Short project summary
* Date or recency indicator
* Link to view the project

Possible project titles include:

* Exterior House Painting in Marietta
* Large Oak Tree Removal in Decatur
* Backyard Paver Patio Installation in Alpharetta
* Interior Repainting Project in Roswell

The homepage should include:

* Search
* Service filters
* Location filters
* Contractor filters
* Recently completed projects
* Featured projects
* Featured contractors
* Popular services
* Popular locations
* Clear explanation of how JobbPulse works
* Homeowner call to action
* Contractor call to action

The homepage should communicate:

> Browse real projects completed by local contractors.

Avoid leading with generic language such as:

> Find trusted local businesses.

The work should come first.

---

## 2. Project Detail Page

Every completed project must have its own permanent public page.

This is the most important page type in the platform.

Each project page should include:

### Project Header

* Project title
* Service category
* City or general location
* Contractor name
* Completion date or approximate timeframe
* Primary image

### Project Gallery

* Before photos
* After photos
* Additional photos
* Clear before-and-after grouping
* Optional comparison slider
* Full-screen gallery view

### Project Story

Generate a readable project description from the contractor’s voice summary.

The description may include:

* Customer problem or project goal
* Condition before work began
* Work performed
* Materials or methods used
* Challenges encountered
* Final result
* General location
* Type of property

Do not expose private customer information or exact residential addresses.

### Project Details

Use structured fields where available:

* Service type
* Project type
* Property type
* City
* Neighborhood or general area
* Approximate project duration
* Materials
* Features
* Completion date

### Contractor Attribution

Clearly show:

* Contractor logo or profile image
* Contractor name
* Short company description
* Services offered
* Service areas
* Link to contractor portfolio
* Request estimate button
* Call button
* Message button when supported

### Lead Form

The project page should include a contextual call to action such as:

> Interested in a project like this?

The inquiry should be routed directly to the contractor who completed the project.

The form should preserve project context so the contractor knows which project inspired the inquiry.

Suggested fields:

* Name
* Phone
* Email
* Project location
* Service needed
* Short project description
* Preferred contact method
* Source project ID

### Related Content

Show:

* Similar projects by the same contractor
* Similar projects in the same city
* Similar projects in the same service category
* Other nearby completed projects

---

## 3. Contractor Portfolio Page

Every contractor should have a public portfolio page.

This page is not merely an About page.

It is the contractor’s automatically updated body of completed work.

The contractor portfolio page should include:

* Company name
* Logo
* Cover image
* Short value proposition
* About the company
* Services offered
* Areas served
* Contact information
* Website
* Phone
* Request estimate button
* Reviews or testimonials when available
* Number of documented projects
* Recent project activity
* Full project gallery
* Project filters
* Service filters
* Location filters

The portfolio should visually emphasize completed projects over marketing copy.

Example:

> Smith Painting
> 47 documented projects
> Serving Marietta, Roswell and East Cobb

The contractor portfolio should grow automatically whenever the contractor publishes a new completed project.

---

## 4. Contractor About Page

Each contractor may also have a separate About page or an About section within the contractor portfolio.

It should include:

* Company story
* Years in business
* Team information
* Licenses or certifications
* Insurance information when provided
* Specialties
* Service philosophy
* Areas served
* Contact details
* Links to project portfolio
* Links to reviews
* Request estimate call to action

The About page should support trust, but it should not replace the project portfolio.

---

## 5. Service Category Pages

Create an index page for each major service category.

Initial categories may include:

* Painting
* Tree Service
* Stump Removal
* Hardscaping
* Landscape Installation
* Flooring
* Fencing
* Deck Building
* Roofing

Each service page should include:

* Service introduction
* Recent projects
* Featured contractors
* Locations where the service is available
* Subcategories
* Search and filters
* Links to relevant service-and-location pages

Example:

> Recent Painting Projects

The project gallery should remain the dominant element.

---

## 6. Location Pages

Create pages for cities and service areas.

Examples:

* Atlanta
* Marietta
* Roswell
* Alpharetta
* Decatur
* Smyrna
* Johns Creek

Each location page should include:

* Recent projects completed in that location
* Services available
* Contractors active in that area
* Popular project categories
* Links to service-and-location pages
* Search and filter controls

Do not publish exact customer addresses.

Locations should be shown at a safe level such as:

* City
* Neighborhood
* ZIP code area
* General service area

---

## 7. Service-and-Location Pages

Support pages that combine a service with a location.

Examples:

* Painters in Marietta
* Tree Removal Projects in Decatur
* Hardscape Contractors in Alpharetta
* Exterior Painting Projects in Roswell

These pages should be generated only when enough genuine project data exists.

Avoid creating thousands of thin or empty pages.

Each service-and-location page should include:

* Real completed projects
* Contractors with relevant experience
* Local service description
* Related nearby locations
* Lead request option
* Relevant filters

Real project inventory must remain the core content.

---

## 8. Search Results Page

Provide a search experience that supports:

* Free-text search
* Service category
* City
* Neighborhood
* Contractor
* Project type
* Recency
* Before-and-after availability

Search results should prioritize projects.

Contractors may appear as a secondary result type.

The system should handle searches such as:

* Exterior painting near Marietta
* Tree removal in Decatur
* Backyard patio projects
* Recent jobs by Smith Painting
* Retaining walls near Alpharetta

---

# Navigation Structure

Recommended primary navigation:

* Browse Projects
* Services
* Locations
* Contractors
* How It Works
* For Contractors

Search should remain visible throughout the site.

On mobile, prioritize:

* Search
* Browse Projects
* Filters
* Contact Contractor

---

# Project Card Requirements

Create a reusable project card component.

Each project card should support:

* Image
* Before-and-after badge
* Project title
* Service
* Location
* Contractor
* Date
* Short summary
* Featured status
* Link to project page

Cards should work in:

* Homepage gallery
* Contractor portfolios
* Service pages
* Location pages
* Search results
* Related project sections

---

# Data Model

Design the data architecture so each project can be connected to one contractor, one primary service and one primary location.

## Contractor

Suggested fields:

* id
* slug
* company_name
* logo
* cover_image
* short_description
* full_about
* phone
* email
* website
* address
* city
* state
* postal_code
* latitude
* longitude
* public_location_precision
* service_areas
* services
* years_in_business
* license_information
* insurance_information
* certifications
* social_links
* active_status
* featured_status
* created_at
* updated_at

## Project

Suggested fields:

* id
* slug
* contractor_id
* title
* short_summary
* full_description
* voice_summary_transcript
* primary_service_id
* additional_service_ids
* project_type
* property_type
* city
* state
* postal_code
* neighborhood
* latitude
* longitude
* public_location_precision
* approximate_duration
* materials
* features
* completion_date
* status
* featured_status
* published_at
* created_at
* updated_at

## Project Media

Suggested fields:

* id
* project_id
* media_type
* file_url
* thumbnail_url
* sequence
* stage
* caption
* alt_text
* visibility
* created_at

The stage field should support:

* before
* during
* after
* additional

## Service

Suggested fields:

* id
* slug
* name
* description
* parent_service_id
* active_status
* project_count

## Location

Suggested fields:

* id
* slug
* city
* state
* county
* postal_code
* neighborhood
* latitude
* longitude
* location_type
* active_status
* project_count

## Lead

Suggested fields:

* id
* contractor_id
* source_project_id
* source_page_type
* source_page_url
* name
* phone
* email
* project_location
* service_requested
* message
* preferred_contact_method
* lead_status
* created_at

---

# Content Relationships

The system must support these relationships:

* Contractor has many projects
* Contractor offers many services
* Contractor serves many locations
* Project belongs to one contractor
* Project has one primary service
* Project may have multiple secondary services
* Project belongs to one public location
* Project has many media assets
* Project may generate many leads
* Service has many projects
* Location has many projects

These relationships should make it possible to dynamically generate galleries, internal links and related content.

---

# Publishing Workflow

Projects will eventually originate from the JobbPulse Contractor App.

The public portfolio must support this lifecycle:

1. Contractor creates a job.
2. Contractor uploads at least three photos.
3. Contractor records a voice summary.
4. JobbPulse generates the project title and description.
5. Contractor reviews the content.
6. Contractor approves the project.
7. Project is published.
8. Project appears automatically on:

   * Its own project page
   * The contractor portfolio
   * Relevant service pages
   * Relevant location pages
   * Relevant service-and-location pages
   * The homepage gallery when appropriate
9. Project may later be updated or unpublished.

Only approved projects should be publicly visible.

Support project statuses such as:

* draft
* processing
* awaiting_review
* approved
* published
* archived
* rejected

---

# Privacy Requirements

Do not publicly display exact residential addresses.

The system must support location obfuscation.

A contractor may record a precise job location internally, but the public page should display only an approved level such as:

* City
* Neighborhood
* ZIP code
* Approximate map area

Project photos must be reviewed for private information where practical.

Allow project media to be flagged or removed.

Do not expose customer names unless explicit permission has been recorded.

---

# Lead Routing

Lead routing is essential.

Every contractor and project page should have a clear contact path.

When a homeowner submits an inquiry from a project page:

* Route the lead to the contractor attached to that project.
* Preserve the source project.
* Record the service and location.
* Notify the contractor.
* Send the lead into the JobbPulse CRM or GoHighLevel workflow.
* Trigger immediate follow-up when configured.
* Record attribution for reporting.

The platform should be able to answer:

* Which page produced the lead?
* Which project produced the lead?
* Which contractor received the lead?
* Which service was requested?
* Was the lead contacted?
* Did the lead book an estimate?
* Did the lead become a customer?

---

# Search Engine Structure

Build the information architecture to support search discovery without creating thin pages.

Each indexable page should have:

* Unique title
* Unique description
* Canonical URL
* Structured headings
* Descriptive image alt text
* Internal links
* Relevant project content
* Contractor attribution
* Service information
* Location information
* Clear call to action

Recommended URL patterns:

* `/projects`
* `/projects/exterior-house-painting-marietta-ga`
* `/contractors/smith-painting`
* `/contractors/smith-painting/about`
* `/services/painting`
* `/locations/marietta-ga`
* `/locations/marietta-ga/painting`

Do not index empty service-and-location combinations.

Do not generate pages solely to target keywords.

Pages should exist because real project inventory supports them.

---

# Admin Requirements

Create an internal administrative interface that supports:

* Contractor management
* Project review
* Project approval
* Project editing
* Media moderation
* Service management
* Location management
* Featured project selection
* Featured contractor selection
* Lead visibility
* Project status management
* Page preview
* Unpublishing
* Duplicate detection
* Privacy review

Administrators should be able to edit AI-generated content before publication.

---

# User Experience Principles

Follow these principles:

## Work First

Lead with project images and completed work.

## Local Relevance

Clearly show where work was completed without exposing private addresses.

## Immediate Trust

Make it easy to see who performed the work and view more of that contractor’s projects.

## Clear Next Step

Every page should provide an obvious path to request similar work.

## Minimal Dead Ends

Every project page should link to related projects, the contractor portfolio, service pages and location pages.

## Mobile First

Most homeowners and contractors will interact with the platform on mobile devices.

## Honest Inventory

Never imply that many contractors or projects exist in an area when they do not.

---

# Initial MVP Scope

The first release should focus on structure rather than visual polish.

Build:

1. Homepage project gallery
2. Project detail pages
3. Contractor portfolio pages
4. Contractor About pages
5. Service category pages
6. Location pages
7. Basic service-and-location pages
8. Search and filters
9. Lead forms and contractor routing
10. Admin project review
11. Responsive mobile layouts
12. Project publishing workflow
13. Safe public location display

Do not prioritize advanced visual branding, animation or an elaborate color palette during the first phase.

Prioritize:

* Clear information architecture
* Correct data relationships
* Reusable components
* Fast page loading
* Mobile usability
* Expandable page structure
* Reliable lead attribution
* Privacy safeguards

---

# Technology Direction

Use:

* Nuxt for the public frontend
* FastAPI for the backend API
* PostgreSQL for structured data
* Object storage for project images and media
* Server-rendered or statically generated public pages where appropriate
* Clean REST or typed API contracts
* Modular reusable frontend components

Suggested Nuxt components:

* `ProjectCard`
* `ProjectGallery`
* `BeforeAfterGallery`
* `ProjectHeader`
* `ProjectDetails`
* `ContractorSummary`
* `ContractorPortfolioGrid`
* `ServiceFilter`
* `LocationFilter`
* `SearchBar`
* `LeadForm`
* `RelatedProjects`
* `FeaturedProjects`
* `FeaturedContractors`
* `ServiceGrid`
* `LocationGrid`
* `ProjectBreadcrumbs`

Suggested backend modules:

* contractors
* projects
* project_media
* services
* locations
* search
* leads
* publishing
* moderation
* attribution
* admin

---

# Deliverables

Produce:

1. Complete information architecture
2. Sitemap
3. Database schema
4. API endpoint plan
5. Page-by-page wireframe descriptions
6. Nuxt component architecture
7. FastAPI module architecture
8. Project publishing workflow
9. Search and filtering logic
10. Lead-routing workflow
11. Privacy and location-obfuscation rules
12. SEO page-generation rules
13. MVP development sequence
14. Acceptance criteria for every page type

Do not begin by choosing colors, fonts or a visual brand direction.

Begin by defining the content structure, relationships, page hierarchy, navigation, publishing flow and lead-routing system.

The finished product should make JobbPulse feel like:

> A living local portfolio of real work completed by local contractors.

The homeowner should browse work first, understand the contractor second and have a clear way to request a similar project.
