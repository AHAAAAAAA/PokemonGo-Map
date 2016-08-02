# Contributing to this Wiki

*This article is about contributing pages and edits to this wiki. For contributing to the map itself see [Development](Development.md).*

Before you can change any files, you'll have to <a class="github-button" href="https://github.com/JonahAragon/PoGoMapWiki/fork" data-icon="octicon-repo-forked" data-count-href="/JonahAragon/PoGoMapWiki/network" data-count-api="/repos/JonahAragon/PoGoMapWiki#forks_count" data-count-aria-label="# forks on GitHub" aria-label="Fork JonahAragon/PoGoMapWiki on GitHub">Fork</a> this repo on GitHub.

## Adding new files

Keep filenames short and to the point (example, [`installation.md`](installation.md)), this filename will **not** be the name displayed on the page.

Always begin your new page with a title:

```
# This is my title
```

This will be shown on the page and should describe what the new page is about. The rest of the file should be written in GitHub Flavored Markdown, following [these guidelines](https://guides.github.com/features/mastering-markdown/) to be formatted correctly. Additionally you should read the Special Formatting section below.

Sidebars will automatically be generated if you have more than 3 sections on your page.

When you are completed with your new page, open [`navigation.md`](navigation.md) and add it under whatever section you feel it fits, following the format of the other links. When you are finished, submit your file as a Pull Request to be reviewed.

## Editing files

Simply edit existing files using [GitHub Flavored Markdown](https://guides.github.com/features/mastering-markdown/) and submit it as a new Pull Request. In addition to GitHub flavored Markdown, you should read the Special Formatting section below.

## Special Formatting

In addition to the GitHub Markdown style guides, there are some special formats you can add to your pages for extra clarification.

### Notes/Warnings:

Any text written that begins with "Note" / "Warning" or "Attention" / "Hint" or "Tip" followed by a ":" or a "!" will in a box. For example, typing:

```
**Note:** This is a note!

**Warning!** This is a warning.

**Tip:** This is a hint.
```

Will appear like so:

**Note:** This is a note!

**Warning!** This is a warning.

**Tip:** This is a hint.

### GitHub Gists

Gists can be added by typing their numerical ID in the following format:

```
[gimmick:gist](5641564)
```

Preview:

[gimmick:gist](5641564)
