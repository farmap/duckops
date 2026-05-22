import os
import pathlib
from datetime import datetime
from typing import Optional

def get_blog_dir() -> pathlib.Path:
    # Resolves from api/src/app/services/blog_mdx.py up to api/src/ -> api/ -> duckops/ -> web/src/content/blog/
    current_file = pathlib.Path(__file__)
    workspace_dir = current_file.parent.parent.parent.parent.parent
    return workspace_dir / "web" / "src" / "content" / "blog"

def generate_blog_mdx(
    post_id: str, 
    slug: str, 
    title: str, 
    content: str, 
    data_path: Optional[str] = None
) -> str:
    blog_dir = get_blog_dir()
    blog_dir.mkdir(parents=True, exist_ok=True)
    file_path = blog_dir / f"{slug}.mdx"
    
    pub_date = datetime.now().strftime("%b %d %Y")
    
    # 1. Frontmatter with placeholder defaults
    mdx_text = f"""---
title: '{title}'
description: 'Automatically generated post for {title}'
pubDate: '{pub_date}'
heroImage: '../../assets/blog-placeholder-2.jpg'
---

"""
    # 2. Component Imports
    mdx_text += "import PostApiData from '../../components/PostApiData.astro';\n"
    if data_path:
        mdx_text += "import MetricsChart from '../../components/MetricsChart.tsx';\n"
    mdx_text += "\n"
    
    # 3. User Content
    mdx_text += f"{content}\n\n"
    
    # 4. Interactive Astro Card
    mdx_text += "## Live API Data\n\n"
    mdx_text += f"<PostApiData id=\"{post_id}\" />\n\n"
    
    # 5. Interactive ECharts Chart (Only if Data Path is set)
    if data_path:
        mdx_text += "## Lakehouse Metrics\n\n"
        mdx_text += f"<MetricsChart slug=\"{slug}\" client:load />\n"
        
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(mdx_text)
        
    return str(file_path)

def delete_blog_mdx(slug: str) -> None:
    blog_dir = get_blog_dir()
    file_path = blog_dir / f"{slug}.mdx"
    try:
        if file_path.exists():
            os.remove(file_path)
            print(f"Deleted MDX file for slug '{slug}' from disk.")
    except Exception as e:
        print(f"Failed to delete MDX file for slug '{slug}': {e}")
