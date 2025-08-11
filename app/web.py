"""Simple Flask interface for planning and publishing articles."""

from __future__ import annotations

from flask import Flask, render_template, request, redirect, url_for, flash

from .perplexity_generator import PerplexityGenerator, PerplexityError
from .medium_publisher import MediumPublisher, MediumError

app = Flask(__name__)
app.secret_key = "auto-blog-secret"

articles: dict[str, str] = {}


def get_generator() -> PerplexityGenerator:
    """Return a cached ``PerplexityGenerator`` instance."""
    global _generator
    if "_generator" not in globals():
        _generator = PerplexityGenerator()
    return _generator


@app.route("/")
def index() -> str:
    """Display trending topics with buttons to create an article."""
    try:
        topics = get_generator().suggest_trending_topics()
    except PerplexityError as exc:
        flash(str(exc), "danger")
        topics = []
    return render_template("index.html", topics=topics)


AUDIENCE_LEVELS = ["beginner", "intermediate", "advanced"]
TONES = [
    "casual",
    "tutorial",
    "storytelling",
    "formal",
    "friendly",
    "professional",
    "practical",
    "conversational",
]
GOALS = [
    "Learn the basics",
    "Build a project",
    "Deep dive",
    "Best practices",
]


@app.route("/create", methods=["GET", "POST"])
def create_article() -> str:
    """Generate an article for a given topic and show it for publishing."""
    if request.method == "POST":
        topic = request.form.get("topic")
        if not topic:
            flash("Missing topic", "warning")
            return redirect(url_for("index"))
        audience = request.form.get("audience_level", "beginner")
        tone = request.form.get("tone", "tutorial")
        goal = request.form.get("goal", "")
        try:
            content = get_generator().generate_article(
                topic,
                audience_level=audience,
                tone=tone,
                goal=goal,
            )
        except PerplexityError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("index"))
        articles[topic] = content
        return render_template("article.html", topic=topic, content=content)
    # GET request: show form with options
    topic = request.args.get("topic")
    if not topic:
        flash("Missing topic", "warning")
        return redirect(url_for("index"))
    return render_template(
        "create.html",
        topic=topic,
        audience_levels=AUDIENCE_LEVELS,
        tones=TONES,
        goals=GOALS,
    )


@app.route("/publish", methods=["POST"])
def publish_article() -> str:
    """Publish the generated article to Medium."""
    topic = request.form.get("topic", "")
    content = request.form.get("content", "")
    try:
        publisher = MediumPublisher()
        publisher.publish_article(title=topic, content_markdown=content)
        flash("Article published to Medium", "success")
    except MediumError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
