# JobbPulse Technology and Platform Stack

## Overview

JobbPulse combines a custom application stack with established marketing, automation and publishing platforms.

The current confirmed stack is:

- Nuxt for the front end
- FastAPI for the back end
- GoHighLevel for Smart Websites, CRM and lead-conversion automation
- Upload-Post for social distribution
- AI services connected through the FastAPI back end

Several infrastructure choices remain open and have not yet been formally locked in.

## Front End

### Nuxt

Nuxt is the planned front-end framework for the custom JobbPulse software.

It will be used to build:

- The mobile-first Contractor App
- Contractor onboarding and account screens
- The Create Job workflow
- Photo upload and management interfaces
- Voice-summary recording and submission
- AI-generated content review and approval screens
- Contractor dashboards
- Job history and publishing status views
- The JobbPulse Directory
- Contractor portfolio pages
- Individual completed-project pages
- Administrative interfaces where appropriate

Nuxt supports a modern component-based front end and can serve both interactive application screens and search-friendly public directory pages.

## Back End

### FastAPI

FastAPI is the planned back-end framework for JobbPulse.

It will manage:

- Authentication and authorization
- Contractor accounts and organizations
- Jobs and completed-project records
- Photo metadata and media references
- Voice-summary uploads and processing
- Transcription requests
- AI content-generation workflows
- Human approval and regeneration logic
- Publishing status and content versions
- Connections to GoHighLevel
- Connections to the social publishing platform
- Smart Website content synchronization
- Directory publishing
- Notifications and reminders
- API access for the Nuxt front end

FastAPI will act as the central orchestration layer connecting the custom JobbPulse experience to outside services.

## Smart Website and Automation Platform

### GoHighLevel

GoHighLevel is the service-delivery platform for the JobbPulse Smart Website and lead-conversion layer.

It will provide or support:

- Contractor websites
- CRM and contact management
- Sales pipelines
- Contact forms
- Lead capture
- Missed-call text back
- Automated SMS follow-up
- AI-powered SMS conversations
- AI phone answering
- Website chat
- Appointment and estimate booking
- Lead nurturing
- Speed-to-lead workflows
- Review-request automation
- Customer reactivation and remarketing
- Phone-number and communication workflows

The Smart Website will also receive approved completed-job content from the custom JobbPulse system so the contractor's gallery, feed or portfolio can update automatically.

GoHighLevel provides the familiar automation and CRM capabilities. The proprietary JobbPulse value sits in the job-capture workflow, content engine, publishing orchestration and owned directory.

## Social Publishing

### Upload-Post

[Upload-Post](https://www.upload-post.com/) is the social publishing provider for distributing approved content to contractors' social accounts.

Its role is to:

- Receive approved social content from JobbPulse
- Publish or schedule content across supported social networks
- Reduce the need to build and maintain separate direct integrations for every social platform
- Support centralized publishing from the Contractor App workflow

The publishing process includes human approval before content is distributed.

JobbPulse talks to Upload-Post through the replaceable `PublishingProvider` adapter. The contractor never has to use the Upload-Post dashboard.

First-ship social destinations (locked):

- Google Business Profile
- Facebook
- Instagram
- TikTok
- YouTube Shorts

Later platforms (Pinterest, LinkedIn, Threads, Nextdoor, and others) stay off the first ship.

## Artificial Intelligence Layer

AI services will be connected through the FastAPI back end.

The AI layer will process:

- Before-and-after photos
- Contractor voice summaries
- Job descriptions
- Service categories
- City and service-area information
- Contractor brand context

It will generate:

- Social media posts
- Completed-project descriptions
- Smart Website portfolio copy
- Directory job-page copy
- Titles, summaries and calls to action
- Alternative content versions when the contractor requests regeneration
- Potential future advertising copy and creative briefs

The specific AI model provider has not yet been formally selected.

## Voice and Transcription

The Contractor App requires voice capture and speech-to-text processing.

The planned workflow is:

```text
Record voice summary in Nuxt interface
→ Upload audio to FastAPI
→ Send audio to transcription provider
→ Store transcript with job record
→ Use transcript as input for AI content generation
```

The specific transcription provider has not yet been locked in.

## Media Storage

JobbPulse must store or manage:

- Before photos
- After photos
- Additional project photos
- Voice recordings
- Generated media derivatives
- Contractor logos and profile images

The exact cloud storage provider has not yet been formally selected.

Likely requirements include:

- Direct and resumable uploads
- Secure access controls
- Image optimization
- Thumbnail generation
- Backup and retention policies
- CDN delivery for public project pages
- Clear ownership and export policies

## Database

The database technology has not yet been formally locked in.

The data model will need to support:

- Users
- Contractor organizations
- Team members
- Jobs
- Job photos
- Voice recordings and transcripts
- Generated content versions
- Approval history
- Publishing destinations
- Social publishing records
- Smart Website synchronization
- Directory pages
- Leads and attribution data
- Service categories
- Cities and service areas

A relational database is the natural fit for these connected records, but no final database choice is confirmed in the current specification.

## Authentication

The authentication provider has not yet been selected.

The system will need role-based access for:

- Contractor owners
- Crew members
- Office staff
- JobbPulse administrators
- Potential agency or partner users

It should also support secure sessions, password recovery, account invitations and organization-level separation.

## Hosting and Deployment

The cloud hosting platform has not yet been formally selected.

The deployment architecture will need to support:

- Nuxt application hosting
- FastAPI services
- Background processing
- Media storage
- Database hosting
- Secure secrets management
- Logging and monitoring
- Automated deployments
- Backups
- Scaling public directory traffic independently from contractor application traffic

## Background Jobs and Workflow Processing

Some JobbPulse processes should run asynchronously, including:

- Audio transcription
- AI content generation
- Image processing
- Publishing to multiple destinations
- Website synchronization
- Social scheduling
- Notifications and reminders
- Retry handling after failed integrations

The specific job queue and worker technology has not yet been selected.

## Core Integration Flow

```text
Nuxt Contractor App
        ↓
FastAPI Back End
        ↓
Photos + Voice Summary + Job Data
        ↓
Transcription and AI Services
        ↓
Human Review and Approval
        ↓
┌─────────────────────┬─────────────────────┬─────────────────────┐
│ Social Publishing   │ GoHighLevel Smart   │ JobbPulse Directory  │
│ via Upload-Post     │ Website             │                     │
└─────────────────────┴─────────────────────┴─────────────────────┘
```

## Ownership and Control

JobbPulse intends to own and control:

- The Contractor App
- The FastAPI application layer
- Contractor and job records
- The content-generation workflow
- Approval and publishing logic
- Contractor profile pages
- Individual completed-project pages
- The JobbPulse Directory
- The accumulated project, performance and marketing data

Third-party platforms will provide supporting capabilities, but the core contractor workflow and owned distribution asset remain under JobbPulse control.

## Confirmed Versus Open Decisions

### Confirmed

- Nuxt front end
- FastAPI back end
- GoHighLevel Smart Website and automation layer
- Upload-Post for social publishing
- Human approval before publishing
- AI connected through the FastAPI back end
- Automatic publishing to social media, Smart Websites and the JobbPulse Directory

### Not Yet Locked In

- Database platform
- Cloud hosting provider
- Object and media storage provider
- Authentication provider
- AI model provider
- Speech-to-text provider
- Background job queue
- Monitoring and observability platform
- Analytics and attribution stack
- Payment processor
