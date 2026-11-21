"""Unit tests for Plant the Moon HTML scraping and deduplication."""

from ptm_meta.scrape import SeasonTarget, discover_extra_targets, parse_awards_html

SAMPLE_HTML = """
<html><body><main>
  <h2>Best in Show Winners</h2>
  <section class="elementor-inner-section">
    <div class="elementor-column">
      <div class="elementor-widget-wrap">
        <div class="elementor-widget-image"><img src="https://plantthemoon.com/wp-content/uploads/2026/05/24974.png"></div>
        <div class="elementor-widget-heading"><h2 class="elementor-heading-title">Team<br>Shonik</h2></div>
        <div class="elementor-widget-text-editor"><div class="elementor-widget-container"><p>Experimental Design</p></div></div>
        <div class="elementor-widget-text-editor"><div class="elementor-widget-container"><p>Effect of Microbial Necromass on Radish Growth</p></div></div>
        <div class="elementor-widget-text-editor"><div class="elementor-widget-container"><p>High School Level</p></div></div>
        <div class="elementor-widget-button"><a href="https://plantthemoon.com/wp-content/uploads/2026/05/Shonik.pdf">Report</a></div>
      </div>
    </div>
    <div class="elementor-column">
      <div class="elementor-widget-wrap">
        <div class="elementor-widget-heading"><h2 class="elementor-heading-title">Smells<br>fishy1!</h2></div>
        <div class="elementor-widget-text-editor"><div class="elementor-widget-container"><p>Plant Growth</p></div></div>
        <div class="elementor-widget-text-editor"><div class="elementor-widget-container"><p>Growing Baby Spinach Using Aquaculture</p></div></div>
        <div class="elementor-widget-text-editor"><div class="elementor-widget-container"><p>High School Level</p></div></div>
        <div class="elementor-widget-button"><a href="https://plantthemoon.com/wp-content/uploads/2026/05/Smellsfishy1.pdf">Report</a></div>
      </div>
    </div>
  </section>
  <h2>State Award Winners</h2>
  <section class="elementor-inner-section">
    <div class="elementor-column">
      <div class="elementor-widget-wrap">
        <div class="elementor-widget-heading"><h2 class="elementor-heading-title">Top IA Team</h2></div>
        <div class="elementor-widget-text-editor"><div class="elementor-widget-container"><p>High School Level</p></div></div>
        <div class="elementor-widget-text-editor"><div class="elementor-widget-container"><p>Smellsfishy1!</p><p><em>Postville, IA</em></p></div></div>
      </div>
    </div>
    <div class="elementor-column">
      <div class="elementor-widget-wrap">
        <div class="elementor-widget-heading"><h2 class="elementor-heading-title">Top FL Team</h2></div>
        <div class="elementor-widget-text-editor"><div class="elementor-widget-container"><p>High School Level</p></div></div>
        <div class="elementor-widget-text-editor"><div class="elementor-widget-container"><p>Terraform Titans</p><p><em>Panama City, FL</em></p></div></div>
      </div>
    </div>
  </section>
</main></body></html>
"""


def test_parse_awards_html_extracts_and_merges() -> None:
    target = SeasonTarget(
        season="Spring 2026",
        slug="spring26",
        year=2026,
        term="Spring",
        order=12,
        track="main",
        url="https://plantthemoon.com/awards-spring26/",
    )
    records = parse_awards_html(SAMPLE_HTML, target)
    assert len(records) == 3

    by_team = {r.team_name: r for r in records}
    assert "Team Shonik" in by_team
    assert by_team["Team Shonik"].has_pdf is True
    assert by_team["Team Shonik"].award_category == "Experimental Design"
    assert by_team["Team Shonik"].pdf_url.endswith("Shonik.pdf")

    # Smells fishy1! should merge Top IA Team state badge and Postville, IA location
    smells = by_team["Smells fishy1!"]
    assert smells.location_state == "IA"
    assert smells.location_city == "Postville"
    assert any("State Award" in b for b in smells.award_badges)

    fl = by_team["Terraform Titans"]
    assert fl.has_pdf is False
    assert fl.location_state == "FL"


def test_discover_extra_targets() -> None:
    html = '<a href="https://plantthemoon.com/awards-fall26/">Fall 26</a><a href="https://plantthemoon.com/jr/awards-fall26/">Jr</a>'
    extra = discover_extra_targets(html, existing_urls=set())
    assert len(extra) == 2
    assert {e.track for e in extra} == {"main", "junior"}
    assert extra[0].season == "Fall 2026"


def test_space_grant_and_top_team_cards() -> None:
    html = """
    <html><body><main>
      <div class="elementor-column"><div class="elementor-widget-wrap">
        <div class="elementor-widget-heading"><h2 class="elementor-heading-title">NASA Space Grant Regional Expansion Project Winners</h2></div>
      </div></div>
      <div class="elementor-column"><div class="elementor-widget-wrap">
        <div class="elementor-widget-heading"><h2 class="elementor-heading-title">FL Space Grant</h2></div>
        <div class="elementor-widget-text-editor"><div class="elementor-widget-container"><p>High School Level</p></div></div>
        <div class="elementor-widget-text-editor"><div class="elementor-widget-container"><p>Lunar Leaf Legends</p><p>GBHS Team A</p></div></div>
      </div></div>
      <div class="elementor-column"><div class="elementor-widget-wrap">
        <div class="elementor-widget-heading"><h2 class="elementor-heading-title">Top MI Team</h2></div>
        <div class="elementor-widget-text-editor"><div class="elementor-widget-container"><p>Middle School Level</p></div></div>
        <div class="elementor-widget-text-editor"><div class="elementor-widget-container"><p>Jefferson Middle School Team 10</p><p><em>Midland, MI</em></p></div></div>
      </div></div>
    </main></body></html>
    """
    target = SeasonTarget(
        season="Fall 2025",
        slug="fall25",
        year=2025,
        term="Fall",
        order=11,
        track="junior",
        url="https://plantthemoon.com/jr/awards-fall25/",
    )
    records = parse_awards_html(html, target)
    names = {r.team_name for r in records}
    assert "NASA Space Grant Regional Expansion Project Winners" not in names
    assert {"Lunar Leaf Legends", "GBHS Team A", "Jefferson Middle School Team 10"} == names
    mi = next(r for r in records if r.team_name == "Jefferson Middle School Team 10")
    assert mi.division == "Middle School Level"
    assert mi.location_state == "MI"

