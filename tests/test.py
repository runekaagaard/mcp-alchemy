import shutil, os, difflib, sys

from mcp_alchemy.server import *

d = dict

GDI1 = """
Connected to sqlite version 3.37.2 database tests/Chinook_Sqlite.sqlite.
"""

ATN1 = "Album, Artist, Customer, Employee, Genre, Invoice, InvoiceLine, MediaType, Playlist, PlaylistTrack, Track"

FTN1 = "MediaType, Playlist, PlaylistTrack, Track"

SD1 = """
Customer:
    CustomerId: primary key, INTEGER, primary_key=1
    FirstName: NVARCHAR(40)
    LastName: NVARCHAR(20)
    Company: NVARCHAR(80), nullable
    Address: NVARCHAR(70), nullable
    City: NVARCHAR(40), nullable
    State: NVARCHAR(40), nullable
    Country: NVARCHAR(40), nullable
    PostalCode: NVARCHAR(10), nullable
    Phone: NVARCHAR(24), nullable
    Fax: NVARCHAR(24), nullable
    Email: NVARCHAR(60)
    SupportRepId: INTEGER, nullable

    Relationships:
      SupportRepId -> Employee.EmployeeId
Track:
    TrackId: primary key, INTEGER, primary_key=1
    Name: NVARCHAR(200)
    AlbumId: INTEGER, nullable
    MediaTypeId: INTEGER
    GenreId: INTEGER, nullable
    Composer: NVARCHAR(220), nullable
    Milliseconds: INTEGER
    Bytes: INTEGER, nullable
    UnitPrice: NUMERIC(10, 2)

    Relationships:
      MediaTypeId -> MediaType.MediaTypeId
      GenreId -> Genre.GenreId
      AlbumId -> Album.AlbumId
"""

EQ1 = """
1. row
AlbumId: 1
Title: For Those About To Rock We Salute You
ArtistId: 1

2. row
AlbumId: 2
Title: Balls to the Wall
ArtistId: 2

Result: 2 rows
"""

BASE2 = """
1. row
CustomerId: 1
FirstName: Luís
LastName: Gonçalves
Company: Embraer - Empresa Brasileira de Aeronáutica S.A.
Address: Av. Brigadeiro Faria Lima, 2170
City: São José dos Campos
State: SP
Country: Brazil
PostalCode: 12227-000
Phone: +55 (12) 3923-5555
Fax: +55 (12) 3923-5566
Email: luisg@embraer.com.br
SupportRepId: 3

2. row
CustomerId: 2
FirstName: Leonie
LastName: Köhler
Company: NULL
Address: Theodor-Heuss-Straße 34
City: Stuttgart
State: NULL
Country: Germany
PostalCode: 70174
Phone: +49 0711 2842222
Fax: NULL
Email: leonekohler@surfeu.de
SupportRepId: 5

3. row
CustomerId: 3
FirstName: François
LastName: Tremblay
Company: NULL
Address: 1498 rue Bélanger
City: Montréal
State: QC
Country: Canada
PostalCode: H2G 1A7
Phone: +1 (514) 721-4711
Fax: NULL
Email: ftremblay@gmail.com
SupportRepId: 3

4. row
CustomerId: 4
FirstName: Bjørn
LastName: Hansen
Company: NULL
Address: Ullevålsveien 14
City: Oslo
State: NULL
Country: Norway
PostalCode: 0171
Phone: +47 22 44 22 22
Fax: NULL
Email: bjorn.hansen@yahoo.no
SupportRepId: 4

5. row
CustomerId: 5
FirstName: František
LastName: Wichterlová
Company: JetBrains s.r.o.
Address: Klanova 9/506
City: Prague
State: NULL
Country: Czech Republic
PostalCode: 14700
Phone: +420 2 4172 5555
Fax: +420 2 4172 5555
Email: frantisekw@jetbrains.com
SupportRepId: 4

6. row
CustomerId: 6
FirstName: Helena
LastName: Holý
Company: NULL
Address: Rilská 3174/6
City: Prague
State: NULL
Country: Czech Republic
PostalCode: 14300
Phone: +420 2 4177 0449
Fax: NULL
Email: hholy@gmail.com
SupportRepId: 5

7. row
CustomerId: 7
FirstName: Astrid
LastName: Gruber
Company: NULL
Address: Rotenturmstraße 4, 1010 Innere Stadt
City: Vienne
State: NULL
Country: Austria
PostalCode: 1010
Phone: +43 01 5134505
Fax: NULL
Email: astrid.gruber@apple.at
SupportRepId: 5

8. row
CustomerId: 8
FirstName: Daan
LastName: Peeters
Company: NULL
Address: Grétrystraat 63
City: Brussels
State: NULL
Country: Belgium
PostalCode: 1000
Phone: +32 02 219 03 03
Fax: NULL
Email: daan_peeters@apple.be
SupportRepId: 4

9. row
CustomerId: 9
FirstName: Kara
LastName: Nielsen
Company: NULL
Address: Sønder Boulevard 51
City: Copenhagen
State: NULL
Country: Denmark
PostalCode: 1720
Phone: +453 3331 9991
Fax: NULL
Email: kara.nielsen@jubii.dk
SupportRepId: 4

10. row
CustomerId: 10
FirstName: Eduardo
LastName: Martins
Company: Woodstock Discos
Address: Rua Dr. Falcão Filho, 155
City: São Paulo
State: SP
Country: Brazil
PostalCode: 01007-010
Phone: +55 (11) 3033-5446
Fax: +55 (11) 3033-4564
Email: eduardo@woodstock.com.br
SupportRepId: 4

11. row
CustomerId: 11
FirstName: Alexandre
LastName: Rocha
Company: Banco do Brasil S.A.
Address: Av. Paulista, 2022
City: São Paulo
State: SP
Country: Brazil
PostalCode: 01310-200
Phone: +55 (11) 3055-3278
Fax: +55 (11) 3055-8131
Email: alero@uol.com.br
SupportRepId: 5

12. row
CustomerId: 12
FirstName: Roberto
LastName: Almeida
Company: Riotur
Address: Praça Pio X, 119
City: Rio de Janeiro
State: RJ
Country: Brazil
PostalCode: 20040-020
Phone: +55 (21) 2271-7000
Fax: +55 (21) 2271-7070
Email: roberto.almeida@riotur.gov.br
SupportRepId: 3

13. row
CustomerId: 13
FirstName: Fernanda
LastName: Ramos
Company: NULL
Address: Qe 7 Bloco G
City: Brasília
State: DF
Country: Brazil
PostalCode: 71020-677
Phone: +55 (61) 3363-5547
Fax: +55 (61) 3363-7855
Email: fernadaramos4@uol.com.br
SupportRepId: 4

14. row
CustomerId: 14
FirstName: Mark
LastName: Philips
Company: Telus
Address: 8210 111 ST NW
City: Edmonton
State: AB
Country: Canada
PostalCode: T6G 2C7
Phone: +1 (780) 434-4554
Fax: +1 (780) 434-5565
Email: mphilips12@shaw.ca
SupportRepId: 5

15. row
CustomerId: 15
FirstName: Jennifer
LastName: Peterson
Company: Rogers Canada
Address: 700 W Pender Street
City: Vancouver
State: BC
Country: Canada
PostalCode: V6C 1G8
Phone: +1 (604) 688-2255
Fax: +1 (604) 688-8756
Email: jenniferp@rogers.ca
SupportRepId: 3
"""

EQ2 = BASE2 + """
Result: showing first 15 rows (output truncated)
"""

EQ2B = BASE2 + """
Result: 59 rows (output truncated)
Full result set url: https://cdn.jsdelivr.net/pyodide/claude-local-files/38d911af2df61f48ae5850491aaa32aff40569233d6aa2a870960a45108067ff.json (format: [[row1_value1, row1_value2, ...], [row2_value1, row2_value2, ...], ...]]) (ALWAYS prefer fetching this url in artifacts instead of hardcoding the values if at all possible)"""

EQ3 = """
Error: (sqlite3.OperationalError) no such column: id
[SQL: SELECT * FROM Customer WHERE id=1]
(Background on this error at: https://sqlalche.me/e/20/e3q8)
"""

EQ4 = """
1. row
AlbumId: 5
Title: Big Ones
ArtistId: 3

Result: 1 rows
"""

EQ5 = """
Error: (sqlite3.OperationalError) near "ZOOP": syntax error
[SQL: ZOOP BOOP LOOP]
(Background on this error at: https://sqlalche.me/e/20/e3q8)
"""

EQMC1 = """
1. row
AlbumId: 1
Title: For Those About To Rock We Salute You
ArtistId: 1

Result: showing first 1 rows (output truncated)
"""

def h1(s):
    print(s)
    print("=" * len(s))
    print()

def diff(wanted_result, actual_result):
    """Show git-like diff between two strings."""
    diff_lines = difflib.unified_diff(wanted_result.splitlines(keepends=True),
                                      actual_result.splitlines(keepends=True), fromfile='wanted_result',
                                      tofile='actual_result', n=3)

    return ''.join(line.replace('\n', '') + '\n' for line in diff_lines)

def test_func(func, tests):
    for args, wanted_result in tests:
        wanted_result = wanted_result.strip()
        actual_result = func(*args)
        if actual_result != wanted_result:
            print(f"{func.__name__}({args})")
            h1("Wanted result")
            print(wanted_result)
            h1("Actual result")
            print(actual_result)
            h1("Diff")
            print(diff(wanted_result, actual_result))
            sys.exit(1)

def main():
    test_func(get_db_info, [([], GDI1)])
    test_func(all_table_names, [([], ATN1)])
    test_func(filter_table_names, [(["a"], FTN1)])
    test_func(schema_definitions, [([["Customer", "Track"]], SD1)])
    test_func(execute_query, [
        (["SELECT * FROM Album LIMIT 2"], EQ1),
        (["SELECT * FROM Customer"], EQ2),
        (["SELECT * FROM Customer WHERE id=1"], EQ3),
        (["SELECT * FROM Album WHERE AlbumId=:AlbumId", d(AlbumId=5)], EQ4),
        (["SELECT * FROM Album WHERE AlbumId=:AlbumId",
          d(AlbumId=-1)], "No rows returned"),
        (["UPDATE Album SET AlbumId=:AlbumId WHERE AlbumId=:AlbumId",
          d(AlbumId=-1)], "Success: 0 rows affected"),
        (["ZOOP BOOP LOOP"], EQ5),
    ])

    # EXECUTE_QUERY_MAX_CHARS setting
    tmp = EXECUTE_QUERY_MAX_CHARS
    tests_set_global("EXECUTE_QUERY_MAX_CHARS", 100)
    test_func(execute_query, [
        (["SELECT * FROM Album LIMIT 2"], EQMC1),
    ])
    tests_set_global("EXECUTE_QUERY_MAX_CHARS", tmp)

    # CLAUDE_LOCAL_FILES_PATH setting
    tmp = "/tmp/mcp-alchemy/claude-local-files"
    os.makedirs(tmp, exist_ok=True)
    tests_set_global("CLAUDE_LOCAL_FILES_PATH", tmp)
    test_func(execute_query, [
        (["SELECT * FROM Customer"], EQ2B),
    ])
    shutil.rmtree(tmp)

if __name__ == "__main__":
    main()
