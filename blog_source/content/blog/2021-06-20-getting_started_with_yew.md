+++
title = "Getting started with Yew"
date = 2021-06-20
slug = "2021-06-20-getting_started_with_yew"
# This is relative to the root!
aliases = [ "2021/06/20/getting_started_with_yew.html", "blog/html/2021/06/20/getting_started_with_yew.html" ]
+++
# Getting started with Yew

Yew is a really nice framework for writing single-page-applications in
Rust, that is then compiled to wasm for running in the browser. For me
it has helped make web development much more accessible to me, but
getting started with it isn\'t always straight forward.

This is the bare-minimum to get a \"hello world\" in your browser - from
there you can build on that foundation to make many more interesting
applications.

## Dependencies

### MacOS

-   Ensure that you have rust, which you can setup with
    [RustUp](https://rustup.rs/).
-   Ensure that you have brew, which you can install from the [Homebrew
    Project](https://brew.sh/). This is used to install other tools.
-   Install wasm-pack. wasm-pack is what drives the rust to wasm build
    process.

```{=html}
<!-- -->
```
    cargo install wasm-pack

-   Install npm and rollup. npm is needed to install rollup, and rollup
    is what takes our wasm and javacript and bundles them together for
    our browser.

```{=html}
<!-- -->
```
    brew install npm
    npm install --global rollup

-   Install miniserve for hosting our website locally during
    development.

```{=html}
<!-- -->
```
    brew install miniserve

## A new project

We can now create a new rust project. Note we use \--lib to indicate
that it\'s a library, not an executable.

    cargo new --lib yewdemo

To start with we\'ll need some boilerplate and helpers to get ourselves
started.

[index.html]{.title-ref} - our default page that will load our wasm to
run. This is our \"entrypoint\" into the site that starts everything
else off. In this case it loads our bundled javascript.

    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>PROJECTNAME</title>
        <script src="/pkg/bundle.js" defer></script>
      </head>
      <body>
      </body>
    </html>

[main.js]{.title-ref} - this is our javascript entrypoint that we\'ll be
using. Remember to change PROJECTNAME to your crate name (ie yewdemo).
This will be combined with our wasm to create the bundle.js file.

    import init, { run_app } from './pkg/PROJECTNAME.js';
    async function main() {
       await init('/pkg/PROJECTNAME_bg.wasm');
       run_app();
      }
    main()

[Cargo.toml]{.title-ref} - we need to extend Cargo.toml with some
dependencies and settings that allows wasm to build and our framework
dependencies.

    [lib]
    crate-type = ["cdylib"]

    [dependencies]
    wasm-bindgen = "^0.2"
    yew = "0.18"

[build_wasm.sh]{.title-ref} - create this file to help us build our
project. Remember to call [chmod +x build_wasm.sh]{.title-ref} so that
you can execute it later.

    #!/bin/sh
    wasm-pack build --target web && \
        rollup ./main.js --format iife --file ./pkg/bundle.js

[src/lib.rs]{.title-ref} - this is a template of a minimal start point
for yew. This has all the stubs in place for a minimal \"hello world\"
website.

    use wasm_bindgen::prelude::*;
    use yew::prelude::*;
    use yew::services::ConsoleService;

    pub struct App {
        link: ComponentLink<Self>,
    }

    impl Component for App {
        type Message = App;
        type Properties = ();

        // This is called when our App is initially created.
        fn create(_: Self::Properties, link: ComponentLink<Self>) -> Self {
            App {
                link,
            }
        }

        fn change(&mut self, _: Self::Properties) -> ShouldRender {
            false
        }

        // Called during event callbacks initiated by events (user or browser)
        fn update(&mut self, msg: Self::Message) -> ShouldRender {
            false
        }

        // Render our content to the page, emitting Html that will be loaded into our
        // index.html's <body>
        fn view(&self) -> Html {
            ConsoleService::log("Hello World!");
            html! {
                <div>
                    <h2>{ "Hello World" }</h2>
                </div>
            }
        }
    }

    // This is the entry point that main.js calls into.
    #[wasm_bindgen]
    pub fn run_app() -> Result<(), JsValue> {
        yew::start_app::<App>();
        Ok(())
    }

## Building your Hello World

Now you can build your project with:

    ./build_wasm.sh

And if you want to see it on your machine in your browser:

    miniserve -v --index index.html .

Navigate to <http://127.0.0.1:8080> to see your Hello World!

## Further Resources

-   [yew guide](https://yew.rs/)
-   [yew api documentation](https://docs.rs/yew/0.18.0/yew/)
-   [yew example
    projects](https://github.com/yewstack/yew/tree/master/examples)
-   [wasm-bindgen
    book](https://rustwasm.github.io/wasm-bindgen/introduction.html)

## Troubleshooting

I made all the following mistakes while writing this blog 😅

### build_wasm.sh - permission denied

    ./build_wasm.sh
    zsh: permission denied: ./build_wasm.sh

You need to run \"chmod +x build_wasm.sh\" so that you can execute this.
Permission denied means that the executable bits are missing from the
file.

### building - \'Could not resolve\'

    ./main.js → ./pkg/bundle.js...
    [!] Error: Could not resolve './pkg/PROJECTNAME.js' from main.js
    Error: Could not resolve './pkg/PROJECTNAME.js' from main.js

This error means you need to edit main.js so that PROJECTNAME matches
your crate name.

### Blank Page in Browser

When you first load your page it may be blank. You can check if a file
is missing or incorrectly named by right clicking the page, select
\'inspect\', and in the inspector go to the \'network\' tab.

From there refresh your page, and see if any files 404. If they do you
may need to rename them or there is an error in yoru main.js. A common
one is:

    PROJECTNAME.wasm: 404

This is because in main.js you may have changed the await init line, and
removed the suffix [\_bg]{.title-ref}.

    # Incorrect
    await init('/pkg/PROJECTNAME.wasm');
    # Correct
    await init('/pkg/PROJECTNAME_bg.wasm');

