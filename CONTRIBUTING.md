# Contributing to Algerian Bio Export Scraper

Thank you for your interest in contributing! This project helps export agencies connect Algerian organic producers with European markets.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version)

### Suggesting Features

We welcome feature suggestions! Please open an issue describing:
- The feature you'd like to see
- Why it would be useful
- How it might work

### Code Contributions

1. **Fork the repository**
2. **Create a branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Test thoroughly**
5. **Commit** (`git commit -m 'Add amazing feature'`)
6. **Push** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

## Development Guidelines

### Code Style

- Follow PEP 8 style guide
- Use meaningful variable names
- Add comments for complex logic
- Keep functions focused and small

### Testing

- Test your changes before submitting
- Ensure scraper works with real websites
- Check that contact extraction works correctly

### Documentation

- Update README.md if needed
- Add docstrings to new functions
- Update guides if behavior changes

## Areas for Contribution

### High Priority

- [ ] Add more Algerian business directories
- [ ] Improve contact extraction accuracy
- [ ] Add support for more product types
- [ ] Enhance duplicate detection
- [ ] Add data validation

### Medium Priority

- [ ] Add export to Excel with formatting
- [ ] Create web interface
- [ ] Add email verification
- [ ] Implement phone number validation
- [ ] Add progress bar

### Low Priority

- [ ] Add multilingual support (Arabic UI)
- [ ] Create Docker container
- [ ] Add API endpoint
- [ ] Create dashboard for results

## Adding New Data Sources

To add a new scraping source:

1. Create a new method in `ExportOpportunityScraper` class
2. Follow the pattern of existing methods
3. Extract contact information using `ContactExtractor`
4. Filter out big companies with `_is_big_company()`
5. Add to the `run()` method

Example:

```python
def scrape_new_source(self):
    """Scrape from new source"""
    logger.info("=== Scraping New Source ===")
    
    # Your scraping logic here
    
    for item in items:
        producer = BioProducer(
            company_name=name,
            phone=phone,
            # ... other fields
            source='New Source'
        )
        self.producers.append(producer)
```

## Adding New Product Types

To add new product categories:

```python
self.target_products = {
    'new_product': ['search', 'terms', 'here'],
}
```

## Code of Conduct

- Be respectful and professional
- Help others learn and grow
- Focus on constructive feedback
- Respect different perspectives

## Questions?

Open an issue or reach out to the maintainers.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping improve this project! 🙏
