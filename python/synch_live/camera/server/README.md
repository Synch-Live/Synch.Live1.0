# Synch.Live camera Flask server

This is not intended to document all the server code—look at the Flask docs to see how to use those APIs.

## CSS

The app uses the CSS framework Tailwind. Tailwind is class-based, but generates rules according to what classes
are actually used in templates. So, you will need to run the Tailwind executable if you add classes and want new rules.

```sh
npm install
npx tailwindcss -i ./styles/input.css -o ./static/output.css --watch
```

Tailwind has [extensive docs](https://tailwindcss.com/docs/installation)—look to those to see what classes to use to get the styles you want.
Remember of course that Tailwind will be looking for the class name in plaintext in a template in order to generate a rule, so consider how to
add classes programatically with care. We also use the forms plugin, which does not yet have solutions for all fields, so bear this in mind
when designing forms.

## Javascript

The app (deliberately) does not have a JS build pipeline, because it is anticipated users will be accessing the site
with evergreen browsers.
Instead it serves raw JS directly from `node_modules`, and there is a URL rule in `__init__.py` to support this (since it's not in `static`).
In addition, the app provides an [import map](http://developer.mozilla.org/en-US/docs/Web/HTML/Element/script/type/importmap#description)
to allow referencing modules with shorter names. The `es-module-shims` module provides a polyfill to browsers without native support for this.

### Turbo

Turbo provides an SPA-like experience without having to use a traditional JS frontend framework. It works by intercepting
navigations and form submissions and dispatching these using JS (thus preserving the DOM) and then swapping out the body
upon response. It is also able to allow the server to send updates to the client after the initial page load using
[Server-sent events](http://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) or
[WebSockets](http://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API).
You should read the docs on [Turbo Drive](https://turbo.hotwired.dev/handbook/drive)
and [Turbo Streams](https://turbo.hotwired.dev/handbook/streams) respectively to see how this works—particularly as regards form submissions.
Turbo Streams in particular are used to provide live updates from `ansible_runner` when running Ansible plays,
and `zeroconf` when listening for advertised mDNS services.
The `turbo-rails` package provides the `turbo-stream-source` element seen in the docs.

### Stimulus

Stimulus is a minimal JS framework to provide interactivity in an isolated and composable way, heavily based on the
[`MutationObserver` API](http://developer.mozilla.org/en-US/docs/Web/API/MutationObserver).
Read [the docs](https://stimulus.hotwired.dev/handbook/introduction) to see how this works, and remember that without Webpack or Rails,
controller registration is manual, in `main.js`.
