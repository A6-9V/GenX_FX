# Contributing to GenX Trading Platform

First off, thank you for considering contributing to the GenX Trading Platform! It's people like you that make this project such a great tool.

Following these guidelines helps to communicate that you respect the time of the developers managing and developing this open source project. In return, they should reciprocate that respect in addressing your issue, assessing changes, and helping you finalize your pull requests.

## How Can I Contribute?

There are many ways to contribute, from writing tutorials or blog posts, improving the documentation, submitting bug reports and feature requests or writing code which can be incorporated into the main project.

### Reporting Bugs

-   **Ensure the bug was not already reported** by searching on GitHub under [Issues](https://github.com/Mouy-leng/GenX_FX/issues).
-   If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/Mouy-leng/GenX_FX/issues/new). Be sure to include a **title and clear description**, as much relevant information as possible, and a **code sample** or an **executable test case** demonstrating the expected behavior that is not occurring.

### Suggesting Enhancements

-   Read through the documentation to understand the current capabilities of the platform.
-   Search on GitHub under [Issues](https://github.com/Mouy-leng/GenX_FX/issues) to see if the enhancement has already been suggested.
-   If it has not, open a new issue. Provide a clear description of the enhancement and why it would be beneficial.

### Your First Code Contribution

Unsure where to begin contributing to the GenX Trading Platform? You can start by looking through these `good-first-issue` and `help-wanted` issues:

-   [Good first issues](https://github.com/Mouy-leng/GenX_FX/labels/good%20first%20issue) - issues which should only require a few lines of code, and a test or two.
-   [Help wanted issues](https://github.com/Mouy-leng/GenX_FX/labels/help%20wanted) - issues which should be a bit more involved than `good-first-issue` issues.

## Development Setup

The `README.md` has a detailed "Quick Start" section. Please refer to it for the initial setup. Here is a summary of the key steps:

```bash
# Clone the repository
git clone https://github.com/Mouy-leng/GenX_FX.git
cd GenX_FX

# Install dependencies
pip3 install --break-system-packages typer rich requests pyyaml python-dotenv

# Make CLI executable
chmod +x genx
```

### Build and Test

The project is a monorepo with a Python backend and a React frontend.

-   **Build**: `npm run build` (builds both frontend and backend)
-   **Dev**: `npm run dev` (runs client + server concurrently)
-   **Test**: `npm test` (Vitest for JS/TS), `python run_tests.py` (pytest for Python)
-   **Lint**: `npm run lint` (ESLint)

## Pull Request Process

1.  Ensure any install or build dependencies are removed before the end of the layer when doing a build.
2.  Update the README.md with details of changes to the interface, this includes new environment variables, exposed ports, useful file locations and container parameters.
3.  Increase the version numbers in any examples and the README.md to the new version that this Pull Request would represent. The versioning scheme we use is [SemVer](http://semver.org/).
4.  You may merge the Pull Request in once you have the sign-off of two other developers, or if you do not have permission to do that, you may request the second reviewer to merge it for you.

## Coding Standards

### Python
- Follow PEP 8.
- Use Pydantic models for data transfer objects.
- Follow FastAPI patterns for API development.
- Use `snake_case` for variables and function names.

### TypeScript/JavaScript
- Use strict typing.
- Use React hooks and functional components.
- Use `camelCase` for variables and function names, and `PascalCase` for components.

### General
- Use absolute imports.
- Add structured exception handling and logging.
- Add comments to your code where necessary.

We look forward to your contributions!
