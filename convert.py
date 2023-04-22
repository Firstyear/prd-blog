

import shutil
import os
import subprocess

OUTPUT = "/tmp/blogconvert"
OUTPUT_BLOG = os.path.join(OUTPUT, "blog")
OUTPUT_PAGES = os.path.join(OUTPUT, "pages")

OLD_PATH = "./blog_source_tinkerer"

def do_convert_blog(blog):
    print("Blog %s" % blog)

    # Get the metadata from the file path
    # _ is the file name here.
    (head, fname) = os.path.split(blog)
    out_fname = fname.replace(".rst", ".md")
    slug_name = fname.replace(".rst", "")

    (head, day) = os.path.split(head)
    (head, month) = os.path.split(head)
    (head, year) = os.path.split(head)

    target_blog = f"{year}-{month}-{day}-{out_fname}"
    target_blog = os.path.join(OUTPUT_BLOG, target_blog)

    print(f"Convert {blog} -> {target_blog}")

    subprocess.run(["pandoc", "-o", target_blog, blog])

    # Now we have to do some post processing
    data = ""
    with open(target_blog, 'r') as file:
        data = file.read()

    data_copy = ""
    for line in data.splitlines():
        if line.startswith(":::"):
            if line.startswith("::: more"):
                pass
            else:
                break
        else:
            data_copy += line
            data_copy += "\n"

    data = data_copy

    # The title is always the first line.
    title = data.split("\n")[0]
    title = title.replace("# ", "")
    title = title.replace("\\", "")
    title = title.replace("\"", "")

    with open(target_blog, 'w') as file:
        file.write(f"""+++
title = "{title}"
date = {year}-{month}-{day}
slug = "{year}-{month}-{day}-{slug_name}"
# This is relative to the root!
aliases = [ "{year}/{month}/{day}/{slug_name}.html", "blog/html/{year}/{month}/{day}/{slug_name}.html" ]
+++
""")
        file.write(data)




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
sort_by = "date"
+++
""")

    with open(os.path.join(OUTPUT_PAGES, "_index.md"), 'w') as file:
        file.write("""
+++
title = "Pages"
template = "oceanic-zen/templates/section.html"
sort_by = "title"
+++
""")

    # Find all the blog posts
    blog_posts = []
    entries = os.walk(OLD_PATH)
    for (dpath, dname, fname) in entries:
        # print("%s %s %s" % (dpath, dname, fname))
        for f in fname:
            if f.endswith('.rst'):
                blog_posts.append(os.path.join(dpath, f))
            else:
                print("Skipping %s" % os.path.join(dpath, f))

    for blog in blog_posts:
        do_convert_blog(blog)






if __name__ == "__main__":
    do_pain()

