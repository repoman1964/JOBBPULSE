<script setup lang="ts">
const config = useRuntimeConfig()
const vslUrl = config.public.vslUrl as string
const vslPoster = config.public.vslPoster as string
const buyUrl = config.public.buyUrl as string

const trades = [
  'Painting',
  'Tree Service',
  'Hardscaping',
  'Landscaping',
  'Flooring',
  'Fences & Decks',
  'Roofing',
  'Remodeling',
]
</script>

<template>
  <div>
    <section class="hero">
      <div class="container hero-grid">
        <div class="hero-copy">
          <p class="eyebrow">For home-services pros</p>
          <h1>Turn every finished job into marketing for the next one.</h1>
          <p class="lead">Take a few before-and-after photos. Talk for about 30 seconds.</p>
          <p class="lead">
            JobbPulse turns the work you already completed into social content, fresh website
            projects, and proof future customers can actually see — then helps you respond when
            they reach out.
          </p>
          <div class="hero-actions">
            <NuxtLink class="btn btn-buy" :to="buyUrl">Get JobbPulse</NuxtLink>
            <a class="btn btn-secondary" href="#watch">Watch the walkthrough</a>
          </div>
          <p class="hero-note">A few taps. A quick description. Back to work.</p>
        </div>
        <div class="phone">
          <img
            src="/images/jobs-page-clay.png"
            width="390"
            height="844"
            alt="JobbPulse Contractor App showing jobs captured from the field"
          >
        </div>
      </div>
    </section>

    <section class="section section-alt" id="watch">
      <div class="container vsl">
        <div class="section-head">
          <p class="eyebrow">Watch</p>
          <h2>See JobbPulse turn a finished job into marketing.</h2>
          <p>
            A short walkthrough of the contractor app — photos, a 30-second voice note, and what
            comes out the other side.
          </p>
        </div>
        <SalesVideo
          :src="vslUrl"
          :poster="vslPoster"
          title="JobbPulse walkthrough"
        />
        <div class="vsl-buy">
          <NuxtLink class="btn btn-buy" :to="buyUrl">I want JobbPulse</NuxtLink>
        </div>
      </div>
    </section>

    <section class="section" id="problem">
      <div class="container">
        <div class="section-head stack">
          <p class="eyebrow">The work is done. Make it keep working.</p>
          <h2>Right now, your camera is full of marketing you don't use.</h2>
          <p>You already did the hard part.</p>
          <p>You sold the job. Did the work. Got the result.</p>
          <p>But once you leave the driveway, most of that proof disappears into your phone.</p>
          <p>
            The photos never get posted.<br>
            The website still shows work from two years ago.<br>
            Another week passes without anything new going online.
          </p>
          <p>
            <strong>JobbPulse fixes that without turning you into the marketing guy.</strong>
          </p>
        </div>
        <div class="problem-grid">
          <article class="card">
            <h3>Your photos stop collecting dust</h3>
            <p class="muted">
              Before-and-after shots become useful proof instead of sitting forgotten on your phone.
            </p>
          </article>
          <article class="card">
            <h3>Your social accounts stay active</h3>
            <p class="muted">
              Real completed jobs become professional content without you stopping to write captions
              or figure out what to post.
            </p>
          </article>
          <article class="card">
            <h3>Your website keeps showing recent work</h3>
            <p class="muted">
              New projects can be added as you finish them, so prospects see what your company is
              doing now — not what it did years ago.
            </p>
          </article>
        </div>
      </div>
    </section>

    <section class="section section-alt" id="how-it-works">
      <div class="container">
        <div class="section-head">
          <p class="eyebrow">This is your part</p>
          <h2 class="headline-one-line">Finish the job. Show off what you did.</h2>
        </div>
        <div class="step-grid">
          <article class="card">
            <div class="step-num">1</div>
            <h3>Create a project for the job</h3>
            <p class="muted">Add the customer area and basic job information. Nothing complicated.</p>
          </article>
          <article class="card">
            <div class="step-num">2</div>
            <h3>Take the pictures</h3>
            <p class="muted">Add before, progress, and after photos as the work happens.</p>
          </article>
          <article class="card">
            <div class="step-num">3</div>
            <h3>Talk for about 30 seconds</h3>
            <p class="muted">
              Tell JobbPulse what you did, what the customer needed, and how the job turned out.
            </p>
          </article>
        </div>
        <div class="thats-it">
          <h3>Then get back to work.</h3>
          <ul class="no-list">
            <li>No captions to write.</li>
            <li>No posts to build.</li>
            <li>No project pages to create.</li>
            <li>No logging into five different marketing tools.</li>
          </ul>
          <p>JobbPulse takes it from there.</p>
        </div>
      </div>
    </section>

    <section class="section" id="what-you-get">
      <div class="container">
        <div class="section-head">
          <p class="eyebrow">JobbPulse takes it from here</p>
          <h2>One finished job becomes proof everywhere it matters.</h2>
          <p>
            After you submit the job, JobbPulse turns the photos and information into marketing
            built around the work you actually performed.
          </p>
          <p>That can include:</p>
        </div>
        <div class="output-grid">
          <div class="output-cards">
            <article class="card">
              <h3>Social media content</h3>
              <p class="muted">
                Professional posts built from your real projects and published across your
                connected social accounts.
              </p>
            </article>
            <article class="card">
              <h3>Fresh website projects</h3>
              <p class="muted">
                Recent jobs added to your website so potential customers can see current examples
                of your work.
              </p>
            </article>
            <article class="card">
              <h3>A JobbPulse project page</h3>
              <p class="muted">
                Each completed job can also become part of your JobbPulse portfolio, giving you
                another place to show the work.
              </p>
            </article>
            <article class="card">
              <h3>Review and customer follow-up</h3>
              <p class="muted">
                JobbPulse can trigger follow-up that helps you collect more reviews and stay in
                touch without relying on memory.
              </p>
            </article>
          </div>
          <div class="phone">
            <img
              src="/images/approval-clay.png"
              width="390"
              height="844"
              alt="Review and approve screen showing social posts and a website project from one job"
            >
          </div>
        </div>
        <div class="closing-lines">
          <p>One job.</p>
          <p>More places showing what your company can do.</p>
          <p>And almost none of the marketing work lands on you.</p>
        </div>
      </div>
    </section>

    <section class="section section-alt" id="why">
      <div class="container why">
        <p class="eyebrow">Why it matters</p>
        <h2>The job you finished today can help sell the one you do next.</h2>
        <p class="lead">Homeowners want proof.</p>
        <p class="lead">They want to see the deck.</p>
        <p class="lead">The kitchen.</p>
        <p class="lead">The roof.</p>
        <p class="lead">The yard.</p>
        <p class="lead">The paint job.</p>
        <p class="lead">The before.</p>
        <p class="lead">The after.</p>
        <p class="lead">
          They want to know you’ve done this kind of work before — and done it well.
        </p>
        <p class="lead">Every completed project gives you another piece of that proof.</p>
        <p class="lead">
          <strong>JobbPulse makes sure it doesn’t die in your camera roll.</strong>
        </p>
        <p class="lead">
          The more work you complete, the more real projects future customers can see when they
          check you out.
        </p>
      </div>
    </section>

    <section class="section" id="lead-desk">
      <div class="container">
        <div class="section-head stack">
          <p class="eyebrow">And when someone reaches out</p>
          <h2>Don’t let a good lead die because you were busy doing the actual work.</h2>
          <p>Marketing only matters if somebody answers when the phone rings.</p>
          <p>And contractors miss calls.</p>
          <p>You’re driving.</p>
          <p>Running equipment.</p>
          <p>Talking to a customer.</p>
          <p>Standing on a roof.</p>
          <p>
            JobbPulse Lead Desk helps keep new inquiries moving even when you can’t respond
            immediately.
          </p>
        </div>
        <div class="lead-grid">
          <article class="card">
            <h3>Missed-call text back</h3>
            <p class="muted">
              If you miss a call, the conversation can start by text instead of ending at voicemail.
            </p>
          </article>
          <article class="card">
            <h3>Fast website response</h3>
            <p class="muted">
              New website inquiries can receive an immediate response instead of waiting until you
              get back to the office.
            </p>
          </article>
          <article class="card">
            <h3>SMS and email follow-up</h3>
            <p class="muted">
              Keep the conversation moving when a homeowner doesn’t respond the first time.
            </p>
          </article>
          <article class="card">
            <h3>Estimate and appointment booking</h3>
            <p class="muted">Give qualified prospects a simple path toward the next step.</p>
          </article>
        </div>
        <div class="closing-lines">
          <p>The goal isn’t to give you another CRM to babysit.</p>
          <p>The goal is to help fewer opportunities fall through the cracks.</p>
        </div>
      </div>
    </section>

    <section class="section" id="who">
      <div class="container">
        <div class="section-head">
          <p class="eyebrow">Built for visual contractors</p>
          <h2>If your finished work looks good, people should be seeing it.</h2>
          <p>
            JobbPulse is built for home-service businesses where the result helps sell the next job.
          </p>
        </div>
        <div class="trade-grid">
          <article v-for="item in trades" :key="item" class="card trade">{{ item }}</article>
        </div>
        <p class="who-note">
          If before-and-after photos help customers understand the quality of your work, JobbPulse
          gives you a simple way to put those photos to work.
        </p>
      </div>
    </section>

    <section class="section close" id="demo">
      <div class="container close-copy">
        <p class="eyebrow">Start simple</p>
        <h2>You do the work. JobbPulse makes sure the next customer sees it.</h2>
        <p class="close-lead">
          Finish the job. Take the pictures. Talk for about 30 seconds. Then get back to the next
          driveway.
        </p>
        <p>
          JobbPulse turns the work you already did into ongoing marketing — social posts, a fresher
          website, and a project page a homeowner can actually look at — and helps you stay on top
          of the opportunities that marketing creates.
        </p>
        <ul class="no-list close-list">
          <li>No content calendar.</li>
          <li>No writing captions at night.</li>
          <li>No remembering to update the website.</li>
          <li>No complicated marketing system to operate.</li>
        </ul>
        <p>Just keep doing good work. We’ll help make sure people see it.</p>
        <p class="hero-note">A few taps. About 30 seconds. Back to work.</p>
        <div class="hero-actions">
          <NuxtLink class="btn btn-buy" :to="buyUrl">Get JobbPulse</NuxtLink>
        </div>
      </div>
    </section>
  </div>
</template>
