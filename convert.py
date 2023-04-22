

import shutil
import os

OUTPUT = "/tmp/blogconvert"
OUTPUT_BLOG = os.path.join(OUTPUT, "blog")
OUTPUT_PAGES = os.path.join(OUTPUT, "pages")

OLD_PATH = "/Users/william/development/prd-blog/blog_source_tinkerer"

def do_pain():
    print("Awww shit here we go again.")

    # Delete the output
    shutil.rmtree(OUTPUT, ignore_errors=True)

    # Create the output structure.
    os.mkdir(OUTPUT)
    os.mkdir(OUTPUT_BLOG)
    os.mkdir(OUTPUT_PAGES)

    # Create the index md's as needed.
    with open(os.path.join(OUTPUT, "_index.md"), 'w') as file:
        file.write("""
+++
template = "oceanic-zen/templates/index.html"
draft = false
sort_by = "date"
# paginate_by = 0
+++
""")

    with open(os.path.join(OUTPUT_BLOG, "_index.md"), 'w') as file:
        file.write("""
+++
title = "Blog"
template = "oceanic-zen/templates/section.html"
+++
""")

    with open(os.path.join(OUTPUT_PAGES, "_index.md"), 'w') as file:
        file.write("""
+++
title = "Pages"
template = "oceanic-zen/templates/section.html"
+++
""")

    # Find all the blog posts



    # 



if __name__ == "__main__":
    do_pain()

