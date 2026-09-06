import requests

USERNAME = "lucienhoang"


def get_user_repos(username):
    """Get all public repositories from a given user."""
    url = f"https://api.github.com/users/{username}/repos"
    r = requests.get(url, timeout=10)
    return r


def get_repo_languages(username, language):
    """Get language byte breakdown for a single repository."""
    url = f"https://api.github.com/repos/{username}/{language}/languages"
    r = requests.get(url, timeout=10)
    return r


def update_readme(sorted_langs, readme_path="README.md"):
    """Update the language stats section in README.md between markers."""
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    start_marker = "<!--LANG-STATS-START-->"
    end_marker = "<!--LANG-STATS-END-->"

    # Build the new stats block as a markdown table.
    lines = ["| Language | Percentage |", "|---|---|"]
    for language, pct in sorted_langs:
        lines.append(f"| {language} | {pct:.1f}% |")
    stats_block = "\n".join(lines)

    start_index = content.index(start_marker) + len(start_marker)
    end_index = content.index(end_marker)

    new_content = (
        content[:start_index] + "\n" + stats_block + "\n" + content[end_index:]
    )

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("README.md updated!")


def main():
    r = get_user_repos(USERNAME)
    repos = r.json()

    total_byte = {}

    for repo in repos:
        repo_name = repo["name"]
        lang_response = get_repo_languages(USERNAME, repo_name)

        if lang_response.status_code == 200:
            languages = lang_response.json()
            for language, byte_count in languages.items():
                total_byte[language] = total_byte.get(language, 0) + byte_count

    # Calculating percentages.
    grand_total = sum(total_byte.values())
    percentage = {
        language: (byte_count / grand_total) * 100
        for language, byte_count in total_byte.items()
    }

    # Sort by percentage, descending.
    sorted_langs = sorted(percentage.items(), key=lambda item: item[1], reverse=True)

    print("\nLanguage breakdown across all repos:")
    for language, pct in sorted_langs:
        print(f"{language}: {pct:.1f}%")

    # Update READEME.md
    update_readme(sorted_langs)


if __name__ == "__main__":
    main()
