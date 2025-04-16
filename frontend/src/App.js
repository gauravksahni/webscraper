// src/App.js
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import axios from 'axios';
import './App.css';

// API configuration
// With Nginx proxy, we use relative paths
const API_BASE_URL = '/api';

// Configure axios defaults
axios.defaults.baseURL = API_BASE_URL;

// Main Home Component
function Home() {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!url) {
      setError('Please enter a URL');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      
      const response = await axios.post('/scrape/', { url });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to scrape the URL. Please try again.');
      console.error('Scraping error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="home-container">
      <h1>Web Scraper</h1>
      <p>Enter a URL to scrape its content</p>
      
      <form onSubmit={handleSubmit} className="scrape-form">
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com"
          className="url-input"
          required
        />
        <button 
          type="submit" 
          className="scrape-button"
          disabled={isLoading}
        >
          {isLoading ? 'Scraping...' : 'Scrape URL'}
        </button>
      </form>

      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}

      {result && (
        <div className="result-container">
          <h2>{result.title}</h2>
          <p><strong>URL:</strong> {result.url}</p>
          <p><strong>Scraped at:</strong> {new Date(result.scraped_at).toLocaleString()}</p>
          <div className="content-preview">
            <h3>Content Preview:</h3>
            <p>{result.content.slice(0, 300)}...</p>
            <Link to={`/page/${result.id}`} className="view-full-button">
              View Full Content
            </Link>
          </div>
        </div>
      )}

      <div className="history-link">
        <Link to="/history">View Scraping History</Link>
      </div>
    </div>
  );
}

// History Component to show previously scraped pages
function History() {
  const [pages, setPages] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchPages();
  }, []);

  const fetchPages = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get('/pages/');
      setPages(response.data);
    } catch (err) {
      setError('Failed to fetch scraped pages');
      console.error('Fetch error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    
    try {
      setIsLoading(true);
      
      if (searchQuery.trim() === '') {
        // If search is empty, fetch all pages
        await fetchPages();
      } else {
        const response = await axios.get(`/search/?query=${encodeURIComponent(searchQuery)}`);
        setPages(response.data);
      }
    } catch (err) {
      setError('Failed to search pages');
      console.error('Search error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="history-container">
      <h1>Scraping History</h1>
      
      <div className="search-container">
        <form onSubmit={handleSearch}>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search content or title..."
            className="search-input"
          />
          <button type="submit" className="search-button">Search</button>
        </form>
      </div>

      {error && <p className="error-message">{error}</p>}
      
      {isLoading ? (
        <p>Loading...</p>
      ) : (
        <div className="pages-list">
          {pages.length === 0 ? (
            <p>No pages found. Try scraping some URLs first.</p>
          ) : (
            pages.map(page => (
              <div key={page.id} className="page-item">
                <h3>{page.title}</h3>
                <p><strong>URL:</strong> <a href={page.url} target="_blank" rel="noopener noreferrer">{page.url}</a></p>
                <p><strong>Scraped:</strong> {new Date(page.scraped_at).toLocaleString()}</p>
                <p><strong>Last accessed:</strong> {new Date(page.last_accessed).toLocaleString()}</p>
                <div className="page-actions">
                  <Link to={`/page/${page.id}`} className="view-button">
                    View Content
                  </Link>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      <div className="back-link">
        <Link to="/">Back to Scraper</Link>
      </div>
    </div>
  );
}

// Page Detail Component
function PageDetail() {
  const [page, setPage] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const pageId = window.location.pathname.split('/').pop();

  useEffect(() => {
    const fetchPageDetail = async () => {
      try {
        setIsLoading(true);
        const response = await axios.get(`/pages/${pageId}`);
        setPage(response.data);
      } catch (err) {
        setError('Failed to fetch page details');
        console.error('Fetch error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPageDetail();
  }, [pageId]);

  if (isLoading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error-message">{error}</div>;
  if (!page) return <div className="not-found">Page not found</div>;

  return (
    <div className="page-detail-container">
      <h1>{page.title}</h1>
      <div className="page-metadata">
        <p><strong>URL:</strong> <a href={page.url} target="_blank" rel="noopener noreferrer">{page.url}</a></p>
        <p><strong>Scraped at:</strong> {new Date(page.scraped_at).toLocaleString()}</p>
        <p><strong>Last accessed:</strong> {new Date(page.last_accessed).toLocaleString()}</p>
      </div>
      
      <div className="content-container">
        <h2>Content:</h2>
        <div className="content-body">
          {page.content.split('\n').map((paragraph, index) => (
            paragraph ? <p key={index}>{paragraph}</p> : <br key={index} />
          ))}
        </div>
      </div>

      <div className="navigation-links">
        <Link to="/history">Back to History</Link>
        <Link to="/">Back to Scraper</Link>
      </div>
    </div>
  );
}

// Main App Component
function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/history" element={<History />} />
          <Route path="/page/:id" element={<PageDetail />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
