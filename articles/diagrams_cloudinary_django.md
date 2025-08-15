---
title: "Integrating Diagrams and Cloudinary in a Django Blog"
seo_description: Generate architecture diagrams with the Diagrams library and host them on Cloudinary within your Django blog.
suggested_tags:
  - Django
  - Diagrams
  - Cloudinary
  - Architecture
  - Tutorials
canonical_url: ""
author: Praveen
---
# Integrating Diagrams and Cloudinary in a Django Blog

Building visual architecture guides alongside your Django tutorials helps readers grasp complex systems quickly. This post walks through generating diagrams using the [Diagrams](https://diagrams.mingrammer.com/) library and hosting those images on [Cloudinary](https://cloudinary.com/) so you can embed them directly into your blog posts.

## Prerequisites

- Python 3.11+
- A Django project
- Cloudinary account with API credentials
- Packages: `diagrams`, `cloudinary`

Install the required packages:

```bash
pip install diagrams cloudinary
```

Configure Cloudinary in your Django settings using environment variables:

```python
# settings.py
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)
```

## Generate a Diagram

Create a management command or utility that builds a diagram image:

```python
# management/commands/build_diagram.py
from diagrams import Diagram
from diagrams.aws.compute import EC2

with Diagram("Simple Setup", filename="diagram", outformat="png"):
    EC2("web")
```

Running this command produces `diagram.png` in your project root.

## Upload to Cloudinary

Immediately after generating the diagram, upload it to Cloudinary and capture the hosted URL:

```python
# utils/cloudinary_upload.py
import cloudinary.uploader

def upload_diagram(path: str) -> str:
    result = cloudinary.uploader.upload(path, folder="blog/diagrams")
    return result["secure_url"]
```

## Embed in Django Templates

Use the returned URL inside your Django templates to display the diagram:

```django
<img src="{{ diagram_url }}" alt="Architecture diagram" />
```

Your view can supply `diagram_url` after calling `upload_diagram`.

## Putting It Together

A simple view combining generation and upload might look like:

```python
from django.shortcuts import render
from .utils import cloudinary_upload
from .management.commands.build_diagram import build


def show_diagram(request):
    build()
    url = cloudinary_upload.upload_diagram("diagram.png")
    return render(request, "diagram.html", {"diagram_url": url})
```

This flow ensures your diagrams are versioned with your code and served via Cloudinary's CDN, keeping your blog fast and maintainable.

## Next Steps

- Add more nodes and clusters in Diagrams to reflect real architectures.
- Automate diagram generation during CI to keep visuals in sync with code changes.
- Explore Cloudinary transformations for responsive image delivery.

Happy diagramming!
