<script setup lang="ts">
const config = useRuntimeConfig()
const vslUrl = config.public.vslUrl as string
const vslPoster = config.public.vslPoster as string
const { show } = useAskModal()

const trades = [
  {
    name: 'Painting',
    before: '/images/trades/painting-before.jpg',
    after: '/images/trades/painting-after.jpg',
  },
  {
    name: 'Tree Service',
    before: '/images/trades/tree-before.jpg',
    after: '/images/trades/tree-after.jpg',
  },
  {
    name: 'Hardscaping',
    before: '/images/trades/hardscape-before.jpg',
    after: '/images/trades/hardscape-after.jpg',
  },
  {
    name: 'Landscaping',
    before: '/images/trades/landscape-before.jpg',
    after: '/images/trades/landscape-after.jpg',
  },
  {
    name: 'Flooring',
    before: '/images/trades/flooring-before.jpg',
    after: '/images/trades/flooring-after.jpg',
  },
  {
    name: 'Fences & Decks',
    before: '/images/trades/deck-before.jpg',
    after: '/images/trades/deck-after.jpg',
  },
  {
    name: 'Roofing',
    before: '/images/trades/roofing-before.jpg',
    after: '/images/trades/roofing-after.jpg',
  },
  {
    name: 'Remodeling',
    before: '/images/trades/remodel-before.jpg',
    after: '/images/trades/remodel-after.jpg',
  },
]

const galleryTrades = [...trades, ...trades]
</script>

<template>
  <div>
    <section class="hero">
      <div class="container hero-grid">
        <div class="hero-copy">
          <p class="eyebrow">For home-services pros</p>
          <h1>Every finished job makes the next job easier to close.</h1>
          <p class="lead">Take a few before-and-after photos. Talk for about 30 seconds.</p>
          <p class="lead">
            JobbPulse turns the work you already completed into social content, fresh website
            projects, and proof future customers can actually see, then helps you respond when
            they reach out.
          </p>
          <div class="hero-actions">
            <button type="button" class="btn btn-buy" @click="show">Ask us about JobbPulse</button>
            <a class="btn btn-secondary" href="#watch">Watch the walkthrough</a>
          </div>
          <p class="hero-note">A few photos. A quick description. Back to work.</p>
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
            A short walkthrough of the contractor app: photos, a 30-second voice note, and what
            comes out the other side.
          </p>
        </div>
        <SalesVideo
          :src="vslUrl"
          :poster="vslPoster"
          title="JobbPulse walkthrough"
        />
        <div class="vsl-buy">
          <button type="button" class="btn btn-buy" @click="show">Ask us about JobbPulse</button>
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
              doing now, not what it did years ago.
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
          <p>That includes:</p>
        </div>
        <figure class="output-visual">
          <img
            src="/images/marketing-everywhere.png?v=2"
            width="1672"
            height="941"
            alt="One completed job becomes a Facebook, Instagram, and Google Business post, local homeowners-group posts, a website carousel item and job page, and a JobbPulse directory listing"
          >
        </figure>
        <div class="output-cards">
          <article class="card">
            <h3>Facebook, Instagram, and Google Business</h3>
            <p class="muted">
              A completed-job post on your Facebook Page, Instagram, and Google Business Profile.
            </p>
          </article>
          <article class="card">
            <h3>Local homeowners groups</h3>
            <p class="muted">
              The same job posted to 3–5 Facebook homeowners and neighborhood groups in your
              service area — where neighbors actually ask for a painter.
            </p>
          </article>
          <article class="card">
            <h3>Your website, updated</h3>
            <p class="muted">
              The job lands on the recent-jobs carousel on your homepage and gets its own
              project page on your site.
            </p>
          </article>
          <article class="card">
            <h3>A JobbPulse directory page</h3>
            <p class="muted">
              Each completed job also becomes a permanent project page on the JobbPulse local
              directory.
            </p>
          </article>
          <article class="card">
            <h3>Posts between jobs</h3>
            <p class="muted">
              Weather, holidays, and seasonal reminders keep those same social accounts and
              groups active so you are not silent for weeks.
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
      </div>
    </section>

    <section class="section" id="lead-desk">
      <div class="container">
        <div class="lead-layout">
          <div class="section-head stack">
            <p class="eyebrow">When someone reaches out</p>
            <h2>Don’t lose a good lead just because you were busy doing the actual work.</h2>
            <p>Marketing only matters if somebody answers when the phone rings.</p>
            <p>And contractors miss calls, all the time.</p>
            <p>You’re driving. Running equipment. Talking to a customer. Standing on a roof.</p>
            <p>
              Lead Desk keeps in touch with current customers and new prospects even when you
              can’t.
            </p>
          </div>
          <figure class="lead-scene">
            <img
              src="/images/lead-desk.jpg?v=2"
              width="864"
              height="1152"
              alt="A painter on a ladder working on a house while a call comes in on the phone in his pocket"
            >
            <figcaption class="lead-toast">
              <p class="lead-toast-label">Lead Desk</p>
              <p>He can’t pick up. The call still gets answered.</p>
            </figcaption>
          </figure>
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
        </div>
      </div>
    </section>

    <section class="section" id="who">
      <div class="container">
        <div class="section-head">
          <p class="eyebrow">Built to be seen</p>
          <h2>If your finished work looks good, people should be seeing it.</h2>
          <p>
            JobbPulse is built for home-service businesses where the result helps sell the next job.
          </p>
        </div>
      </div>
      <div class="trade-gallery" aria-label="Before and after project gallery">
        <div class="trade-track">
          <article v-for="(item, index) in galleryTrades" :key="`${item.name}-${index}`" class="trade-shot">
            <div class="trade-split">
              <img :src="item.before" :alt="`Before ${item.name} project`" width="720" height="480">
              <img :src="item.after" :alt="`After ${item.name} project`" width="720" height="480">
            </div>
            <span class="trade-badge">{{ item.name }}</span>
            <span class="ba-label ba-before">Before</span>
            <span class="ba-label ba-after">After</span>
          </article>
        </div>
      </div>
      <div class="container">
        <p class="who-note">
          If before-and-after photos help customers understand the quality of your work, JobbPulse gives you a simple way to put those photos to work.
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
          JobbPulse turns the work you already did into ongoing marketing: Facebook, Instagram, and
          Google Business posts, 3–5 local homeowners groups, a fresher website with a page per job,
          and a JobbPulse directory listing. Between jobs it keeps those social accounts from going
          quiet. It also helps you stay on top of the opportunities that marketing creates.
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
          <button type="button" class="btn btn-buy" @click="show">Ask us about JobbPulse</button>
        </div>
      </div>
    </section>
  </div>
</template>
