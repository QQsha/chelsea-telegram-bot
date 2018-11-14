import pytest
import psycopg2

import chelsea_bot as cb

URL = "https://www.dailymail.co.uk/sport/football/article-6386163/Olivier-Giroud-voice-Green-Goblin-new-Spiderman-film.html"

GOOD_TEXT = "'He's on the radar': Mason Mount to be tracked by England while \
                    on loan from Chelsea at Derby, says Frank Lampard."

BAD_TEXT = "Follow our RSS feed"


def test_db_connect():
    conn, cursor = cb.con_postgres()
    assert isinstance(conn, psycopg2.extensions.connection)
    assert isinstance(cursor, psycopg2.extensions.cursor)


def test_percentage():
    result = cb.percentage(40, 100)
    assert result == 40


@pytest.mark.parametrize("caption, output", [(GOOD_TEXT, True), (BAD_TEXT, False)])
def test_caption_filter(caption, output):
    result = cb.caption_filter(caption)
    assert result == output


def test_get_content():
    result = cb.scrapper(URL)
    output = (
        "Chelsea striker Olivier Giroud to voice the Green Goblin in new Spider-Man film while PSG's Presnel Kimpembe also lands role in French version",
        "https://i.dailymail.co.uk/1s/2018/11/13/21/6145336-0-image-a-84_1542143431774.jpg"
    )
    assert result == output
