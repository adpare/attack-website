// Require necessary libraries
const $ = require('jquery');

/**
 * It is important that the `.js` file extension be included for local imports, otherwise webpack won't be able to
 * resolve it. i.e., webpack will throw an error like the following:
 *
 * ERROR in ./src/search.js 12:0-20
 * Module not found: Error: Can't resolve './settings' in '/foo/bar/attack-website/attack-search/src'
 */

// Import required modules with the correct file extension
const { baseURL } = require('./settings.js');
const Debouncer = require('./debouncer.js');
const SearchService = require('./search-service.js');

// Import required components
const {
  searchBody,
  searchOverlay,
  searchInput,
  searchParsingIcon,
  searchOpenTrigger,
  closeButton,
  loadMoreResultsButton,
} = require('./components.js');

/**
 * FlexSearch.registerMatcher({REGEX: REPLACE})
 * Enables FlexSearch to globally replace RegEx matches.
 * Here, we use it to augment the "&" in ATT&CK, so searches for "attack" will still match "ATT&CK" and vice versa.
 */
// TODO: Figure out how to do this is v0.7.31
// flexsearch.default.registerMatcher({
//   'ATT&CK': 'ATTACK',
//   ATTACK: 'ATT&CK',
// });

// Check browser types
// const isChromium = window.chrome;
// const isEdgeChromium = isChromium && navigator.userAgent.indexOf('Edg') != -1;
// const isGoogleChrome = !!(isChromium && !isEdgeChromium);

// Open search overlay
const openSearch = function () {
  searchBody.hide();
  searchOverlay.show();
  searchOverlay.removeClass('hidden');
  searchInput.focus();
};

// Close search overlay
const closeSearch = function () {
  searchInput.val('');
  searchOverlay.hide();
  searchOverlay.addClass('hidden');
};

// Variable to check if search service is loaded
let searchServiceIsLoaded = false;

// Initialize the search service
async function initializeSearchService() {
  console.debug('Initializing search service...');
  searchParsingIcon.show();

  const saved_uuid = localStorage.getItem('saved_uuid');
  console.debug(`Retrieved the saved_uuid from localStorage: ${saved_uuid}`);

  // Check if the browser is not Google Chrome and the documents are already cached
  if ('indexedDB' in window) {
    if (saved_uuid && saved_uuid === build_uuid) {
      // Restore search service from IndexedDB
      try {
        console.debug('Initializing SearchService (assume documents already cached)...');
        searchService = new SearchService('search-results', saved_uuid);
        await searchService.initializeAsync(null);
        console.debug('SearchService is initialized.');
      } catch (error) {
        console.error('Failed to initialize SearchService:', error);
        searchServiceIsLoaded = false;
      } finally {
        searchParsingIcon.hide();
        searchServiceIsLoaded = true;
      }
    }
    else {
      // Initialize search service from scratch
      console.debug('Documents not cached yet.');

      // Fetch index.json if documents are not cached
      $.ajax({
        url: `${baseURL}/index.json`,
        dataType: 'json',
        async success(data) {
          try {
            console.debug('Retrieved and processed index.json.');
            console.debug('Initializing SearchService...');

            searchService = new SearchService('search-results', build_uuid);
            await searchService.initializeAsync(data);

            localStorage.setItem("saved_uuid", build_uuid);

            console.debug('SearchService is initialized.');
            searchParsingIcon.hide();
          } catch (error) {
            console.error('Failed to initialize SearchService:', error);
            searchServiceIsLoaded = false;
          } finally {
            searchParsingIcon.hide();
            searchServiceIsLoaded = true;
          }
        },
      });
    }
  }
  else {
    // Disable the search button and display an error icon with a hover effect that displays a message/explanation
    console.error('Search is only available in browsers that support IndexedDB. Please try using Firefox, Chrome, Safari, or another browser that supports IndexedDB.');
    searchInput.prop('disabled', true);
    searchOpenTrigger.prop('disabled', true);
  }
}

// Declare search service variable
let searchService;

// Perform a search using the search service
const search = async function (query) {
  console.debug(`search -> Received search query: ${query}`);

  // Wait until the search service is loaded
  while (!searchServiceIsLoaded) {
    console.debug('search -> search index is not loaded...');
    searchParsingIcon.show();
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  console.debug(`Executing search: ${query}`);
  await searchService.query(query);
  searchParsingIcon.hide();
};

// Instantiate a debouncer
const debounce = new Debouncer(300);

// Set up event handlers for closing search
searchOverlay.on('click', function (e) {
  if (e.target != this) return; // don't close for children
  closeSearch();
});
$(document).keyup((e) => {
  e.key === 'Escape' ? closeSearch() : null;
});

// Set up event handler for close button
closeButton.on('click', closeSearch);

// Set up event handlers for opening search
searchOpenTrigger.on('click', openSearch);

// Set up event handler for search input
searchInput.on('input', (e) => {
  console.log(`Executing search on input: ${e.target.value}`);
  debounce.debounce(() => {
    console.log(`debounce callback: ${e.target.value}`);
    search(e.target.value);
  });
});

// Set up event handler for load more results button
loadMoreResultsButton.on('click', () => {
  if (searchService) searchService.loadMoreResults();
  loadMoreResultsButton.blur(); // onfocus
});

// Add compatibility patches for Internet Explorer
if (!String.prototype.includes) {
  String.prototype.includes = function (search, start) {
    if (typeof start !== 'number') {
      start = 0;
    }
    if (start + search.length > this.length) {
      return false;
    }
    return this.indexOf(search, start) !== -1;
  };
}
if (typeof String.prototype.endsWith !== 'function') {
  String.prototype.endsWith = function (suffix) {
    return this.indexOf(suffix, this.length - suffix.length) !== -1;
  };
}

// Log that search module is loaded
console.debug('search module is loaded.');

// Initialize the search service when the module loads
initializeSearchService();

