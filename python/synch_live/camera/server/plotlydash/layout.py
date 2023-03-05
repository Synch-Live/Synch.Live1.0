"""Plotly Dash HTML layout override."""

html_layout = """
<!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
        </head>
        <body>
        <header>
            <ul class="text-2xl font-medium flex flex-row gap-4 items-center">
                    <h1 style="font-family:helvetica;">Synch.Live Trajectories animation</h1>
            </ul>
        </header>

            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
"""