"""Level 3: Parse LLM output to structured graph/claims data.

This script demonstrates parsing the text output from an LLM
into structured Entity, Relationship, and Claim objects.

Example:
    >>> from use_rag import parse_graph_output
    >>> llm_output = '''("entity"<|>APPLE INC<|>ORGANIZATION<|>Tech company)
    ... ##
    ... ("entity"<|>STEVE JOBS<|>PERSON<|>Co-founder)
    ... ##
    ... ("relationship"<|>STEVE JOBS<|>APPLE INC<|>Founded<|>9)
    ... <|COMPLETE|>'''
    >>> entities, relationships = parse_graph_output(llm_output)
"""

from use_rag import parse_graph_output, parse_claims_output


if __name__ == "__main__":
    # Demo parsing
    graph_output = """("entity"<|>APPLE INC<|>ORGANIZATION<|>A technology company that designs and manufactures consumer electronics)
##
("entity"<|>STEVE JOBS<|>PERSON<|>Co-founder and former CEO of Apple Inc)
##
("entity"<|>CUPERTINO<|>GEO<|>City in California where Apple is headquartered)
##
("relationship"<|>STEVE JOBS<|>APPLE INC<|>Steve Jobs co-founded Apple Inc<|>9)
##
("relationship"<|>APPLE INC<|>CUPERTINO<|>Apple Inc is headquartered in Cupertino<|>8)
<|COMPLETE|>"""

    print("=" * 60)
    print("PARSED GRAPH OUTPUT")
    print("=" * 60)
    entities, relationships = parse_graph_output(graph_output)

    print("\nEntities:")
    for e in entities:
        print(f"  - {e.name} ({e.type}): {e.description[:50]}...")

    print("\nRelationships:")
    for r in relationships:
        print(f"  - {r.source} -> {r.target} (weight={r.weight}): {r.description}")

    claims_output = """(COMPANY A<|>GOVERNMENT AGENCY B<|>ANTI-COMPETITIVE PRACTICES<|>TRUE<|>2022-01-10T00:00:00<|>2022-01-10T00:00:00<|>Company A was found to engage in anti-competitive practices<|>According to an article, Company A was fined for bid rigging)
##
(PERSON C<|>NONE<|>CORRUPTION<|>SUSPECTED<|>2015-01-01T00:00:00<|>2015-12-30T00:00:00<|>Person C was suspected of corruption<|>Person C was suspected of engaging in corruption activities in 2015)
<|COMPLETE|>"""

    print("\n" + "=" * 60)
    print("PARSED CLAIMS OUTPUT")
    print("=" * 60)
    claims = parse_claims_output(claims_output)

    print("\nClaims:")
    for c in claims:
        print(f"  - {c.subject} | {c.type} | {c.status}")
        print(f"    Object: {c.object}")
        print(f"    Dates: {c.start_date} to {c.end_date}")
