"""
LinkedIn Page Scraper using Playwright
Scrapes LinkedIn company pages for page info, posts, comments, and employees
"""
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError
from playwright.async_api import BrowserContext

from linkedin_insights.utils.config import settings

logger = logging.getLogger(__name__)


class LinkedInPageScraper:
    """LinkedIn page scraper using Playwright"""
    
    def __init__(self):
        self.timeout = settings.SCRAPER_TIMEOUT
        self.retry_attempts = settings.SCRAPER_RETRY_ATTEMPTS
        self.headless = settings.SCRAPER_HEADLESS
        self.page_load_timeout = settings.SCRAPER_PAGE_LOAD_TIMEOUT
        self.navigation_timeout = settings.SCRAPER_NAVIGATION_TIMEOUT
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
    
    async def scrape_page(self, page_id: str) -> Dict[str, Any]:
        """
        Scrape LinkedIn page by page ID
        
        Args:
            page_id: Last part of LinkedIn company URL (e.g., 'acme-corp' from linkedin.com/company/acme-corp)
        
        Returns:
            Dictionary with page info, posts, comments, and employees
        """
        page_url = f"https://www.linkedin.com/company/{page_id}"
        logger.info(f"Scraping LinkedIn page: {page_url}")
        
        try:
            async with async_playwright() as p:
                # Launch browser
                self.browser = await p.chromium.launch(
                    headless=self.headless,
                    args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
                )
                
                # Create context with realistic user agent
                self.context = await self.browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                
                page = await self.context.new_page()
                page.set_default_timeout(self.page_load_timeout)
                
                # Navigate to page with retry logic
                page_data = await self._navigate_with_retry(page, page_url)
                
                if not page_data:
                    return self._create_error_response("Page not found or inaccessible")
                
                # Scrape page information
                page_info = await self._scrape_page_info(page, page_id, page_url)
                
                # Scrape posts
                posts = await self._scrape_posts(page, limit=20)
                
                # Scrape comments for each post
                for post in posts:
                    post_id = post.get('post_id', '')
                    comments = await self._scrape_post_comments(page, post_id, limit=10)
                    post['comments'] = comments
                
                # Scrape employees
                employees = await self._scrape_employees(page, page_id)
                
                await self.browser.close()
                
                return {
                    'page_info': page_info,
                    'posts': posts,
                    'employees': employees,
                    'scraped_at': datetime.utcnow().isoformat()
                }
        
        except PlaywrightTimeoutError as e:
            logger.error(f"Timeout error scraping page {page_id}: {str(e)}")
            return self._create_error_response(f"Timeout while scraping page: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error scraping page {page_id}: {str(e)}", exc_info=True)
            return self._create_error_response(f"Error scraping page: {str(e)}")
        
        finally:
            if self.browser:
                await self.browser.close()
    
    async def _navigate_with_retry(self, page: Page, url: str) -> Optional[Dict[str, Any]]:
        """Navigate to page with retry logic"""
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"Navigating to {url} (attempt {attempt + 1}/{self.retry_attempts})")
                response = await page.goto(url, wait_until='networkidle', timeout=self.navigation_timeout)
                
                if response and response.status == 404:
                    logger.warning(f"Page not found (404): {url}")
                    return None
                
                if response and response.status >= 400:
                    logger.warning(f"HTTP error {response.status}: {url}")
                    if attempt < self.retry_attempts - 1:
                        await page.wait_for_timeout(2000)  # Wait before retry
                        continue
                    return None
                
                # Check if page loaded successfully
                await page.wait_for_load_state('domcontentloaded', timeout=10000)
                
                # Check for "Page not found" or similar error messages
                page_content = await page.content()
                if 'not found' in page_content.lower() or 'doesn\'t exist' in page_content.lower():
                    logger.warning(f"Page not found based on content: {url}")
                    return None
                
                return {'status': 'success', 'url': url}
            
            except PlaywrightTimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1}/{self.retry_attempts}")
                if attempt < self.retry_attempts - 1:
                    await page.wait_for_timeout(2000)
                    continue
                return None
            
            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1}: {str(e)}")
                if attempt < self.retry_attempts - 1:
                    await page.wait_for_timeout(2000)
                    continue
                return None
        
        return None
    
    async def _scrape_page_info(self, page: Page, page_id: str, page_url: str) -> Dict[str, Any]:
        """Scrape LinkedIn page information"""
        try:
            # Wait for main content to load
            await page.wait_for_selector('h1, [data-test-id="company-name"]', timeout=10000)
            
            # Extract page name
            name = await self._extract_text(
                page,
                'h1, [data-test-id="company-name"], .org-top-card-summary__title'
            )
            
            # Extract LinkedIn internal ID (from data attributes or URL)
            linkedin_internal_id = None
            try:
                # Try to get from data attributes
                element = await page.query_selector('[data-test-id="company-name"]')
                if element:
                    linkedin_internal_id = await element.get_attribute('data-entity-urn')
                    if linkedin_internal_id:
                        # Extract ID from URN format: urn:li:fs_company:123456
                        match = re.search(r':(\d+)$', linkedin_internal_id)
                        if match:
                            linkedin_internal_id = match.group(1)
            except:
                pass
            
            # Extract profile image
            profile_image_url = await self._extract_attribute(
                page,
                '.org-top-card-primary-content__logo img, .org-top-card-summary__image img',
                'src'
            )
            
            # Extract description
            description = await self._extract_text(
                page,
                '.org-top-card-summary-info-list__info-item, .break-words'
            )
            
            # Extract website
            website = await self._extract_attribute(
                page,
                'a[data-test-id="website"]',
                'href'
            )
            
            # Extract industry
            industry = await self._extract_text(
                page,
                '[data-test-id="industry"], .org-top-card-summary-info-list__info-item'
            )
            
            # Extract total followers
            followers_text = await self._extract_text(
                page,
                '[data-test-id="followers-count"], .org-top-card-summary-info-list__info-item'
            )
            total_followers = self._parse_number(followers_text) if followers_text else None
            
            # Extract headcount
            headcount_text = await self._extract_text(
                page,
                '[data-test-id="headcount"], .org-top-card-summary-info-list__info-item'
            )
            head_count = self._parse_number(headcount_text) if headcount_text else None
            
            # Extract specialities
            specialities = await self._extract_text(
                page,
                '[data-test-id="specialities"], .org-top-card-summary-info-list__info-item'
            )
            
            return {
                'page_id': page_id,
                'name': name or 'Unknown',
                'url': page_url,
                'linkedin_internal_id': linkedin_internal_id,
                'profile_image_url': profile_image_url,
                'description': description,
                'website': website,
                'industry': industry,
                'total_followers': total_followers,
                'head_count': head_count,
                'specialities': specialities
            }
        
        except Exception as e:
            logger.error(f"Error scraping page info: {str(e)}")
            return {
                'page_id': page_id,
                'name': None,
                'url': page_url,
                'linkedin_internal_id': None,
                'profile_image_url': None,
                'description': None,
                'website': None,
                'industry': None,
                'total_followers': None,
                'head_count': None,
                'specialities': None
            }
    
    async def _scrape_posts(self, page: Page, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape latest posts from the page"""
        posts = []
        
        try:
            # Scroll to load posts
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)
            
            # Try multiple selectors for posts
            post_selectors = [
                '.feed-shared-update-v2',
                '.update-components-actor',
                '[data-test-id="update"]',
                '.occludable-update'
            ]
            
            post_elements = []
            for selector in post_selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    post_elements = elements[:limit]
                    break
            
            for i, element in enumerate(post_elements[:limit]):
                try:
                    post_data = await self._extract_post_data(page, element, i)
                    if post_data:
                        posts.append(post_data)
                except Exception as e:
                    logger.warning(f"Error extracting post {i}: {str(e)}")
                    continue
            
            # If no posts found with selectors, try alternative method
            if not posts:
                posts = await self._scrape_posts_alternative(page, limit)
        
        except Exception as e:
            logger.error(f"Error scraping posts: {str(e)}")
        
        return posts[:limit]
    
    async def _extract_post_data(self, page: Page, element: Any, index: int) -> Optional[Dict[str, Any]]:
        """Extract data from a single post element"""
        try:
            # Extract post ID (from data attributes or generate from index)
            post_id = await element.get_attribute('data-urn') or f"post_{index}_{datetime.utcnow().timestamp()}"
            
            # Extract content
            content_element = await element.query_selector('.feed-shared-text, .update-components-text')
            content = await content_element.inner_text() if content_element else None
            
            # Extract like count
            like_element = await element.query_selector('[data-test-id="social-actions__reactions-count"], .social-actions__reactions-count')
            like_text = await like_element.inner_text() if like_element else "0"
            like_count = self._parse_number(like_text)
            
            # Extract comment count
            comment_element = await element.query_selector('[data-test-id="social-actions__comments-count"], .social-actions__comments-count')
            comment_text = await comment_element.inner_text() if comment_element else "0"
            comment_count = self._parse_number(comment_text)
            
            # Extract timestamp
            time_element = await element.query_selector('time, .feed-shared-actor__sub-description')
            posted_at = None
            if time_element:
                datetime_str = await time_element.get_attribute('datetime')
                if datetime_str:
                    try:
                        posted_at = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                    except:
                        pass
                if not posted_at:
                    time_text = await time_element.inner_text()
                    posted_at = self._parse_relative_time(time_text)
            
            if not posted_at:
                posted_at = datetime.utcnow()
            
            return {
                'post_id': post_id,
                'content': content,
                'like_count': like_count or 0,
                'comment_count': comment_count or 0,
                'posted_at': posted_at.isoformat() if isinstance(posted_at, datetime) else posted_at
            }
        
        except Exception as e:
            logger.warning(f"Error extracting post data: {str(e)}")
            return None
    
    async def _scrape_posts_alternative(self, page: Page, limit: int) -> List[Dict[str, Any]]:
        """Alternative method to scrape posts using page evaluation"""
        try:
            posts_data = await page.evaluate("""
                () => {
                    const posts = [];
                    const postElements = document.querySelectorAll('.feed-shared-update-v2, .update-components-actor');
                    
                    postElements.forEach((el, index) => {
                        if (posts.length >= 20) return;
                        
                        const content = el.querySelector('.feed-shared-text, .update-components-text')?.innerText || '';
                        const likeText = el.querySelector('[data-test-id="social-actions__reactions-count"]')?.innerText || '0';
                        const commentText = el.querySelector('[data-test-id="social-actions__comments-count"]')?.innerText || '0';
                        const timeEl = el.querySelector('time');
                        const datetime = timeEl?.getAttribute('datetime') || new Date().toISOString();
                        
                        posts.push({
                            post_id: el.getAttribute('data-urn') || `post_${index}`,
                            content: content,
                            like_count: parseInt(likeText.replace(/[^0-9]/g, '')) || 0,
                            comment_count: parseInt(commentText.replace(/[^0-9]/g, '')) || 0,
                            posted_at: datetime
                        });
                    });
                    
                    return posts;
                }
            """)
            
            return posts_data or []
        
        except Exception as e:
            logger.error(f"Error in alternative post scraping: {str(e)}")
            return []
    
    async def _scrape_post_comments(self, page: Page, post_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Scrape comments for a specific post"""
        comments = []
        
        try:
            # Find the post element and click to expand comments
            post_element = await page.query_selector(f'[data-urn="{post_id}"]')
            if not post_element:
                return comments
            
            # Try to find and click "Show comments" or similar button
            show_comments_button = await post_element.query_selector(
                'button[aria-label*="comment"], .comments-comments-list__show-previous-page'
            )
            
            if show_comments_button:
                await show_comments_button.click()
                await page.wait_for_timeout(2000)
            
            # Extract comments
            comment_elements = await post_element.query_selector_all(
                '.comments-comment-item, .comment-item, [data-test-id="comment"]'
            )
            
            for i, comment_element in enumerate(comment_elements[:limit]):
                try:
                    author_name = await self._extract_text_from_element(
                        comment_element,
                        '.comment-author, .comments-post-meta__actor-name'
                    )
                    
                    content = await self._extract_text_from_element(
                        comment_element,
                        '.comment-content, .comments-comment-item__main-content'
                    )
                    
                    time_element = await comment_element.query_selector('time')
                    created_at = None
                    if time_element:
                        datetime_str = await time_element.get_attribute('datetime')
                        if datetime_str:
                            try:
                                created_at = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                            except:
                                pass
                    
                    if not created_at:
                        created_at = datetime.utcnow()
                    
                    comment_id = await comment_element.get_attribute('data-comment-id') or f"comment_{i}_{datetime.utcnow().timestamp()}"
                    
                    if author_name and content:
                        comments.append({
                            'comment_id': comment_id,
                            'author_name': author_name,
                            'content': content,
                            'created_at': created_at.isoformat() if isinstance(created_at, datetime) else created_at
                        })
                
                except Exception as e:
                    logger.warning(f"Error extracting comment {i}: {str(e)}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping comments for post {post_id}: {str(e)}")
        
        return comments[:limit]
    
    async def _scrape_employees(self, page: Page, page_id: str) -> List[Dict[str, Any]]:
        """Scrape employees/people working at the company"""
        employees = []
        
        try:
            # Navigate to people page
            people_url = f"https://www.linkedin.com/company/{page_id}/people/"
            
            try:
                await page.goto(people_url, wait_until='networkidle', timeout=self.navigation_timeout)
                await page.wait_for_timeout(2000)
            except:
                logger.warning(f"Could not navigate to people page: {people_url}")
                return employees
            
            # Scroll to load more employees
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)
            
            # Extract employee elements
            employee_selectors = [
                '.org-people-profile-card',
                '.org-people__card-spacing',
                '[data-test-id="people-card"]',
                '.org-people-profile-card__profile-info'
            ]
            
            employee_elements = []
            for selector in employee_selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    employee_elements = elements
                    break
            
            for element in employee_elements:
                try:
                    name = await self._extract_text_from_element(
                        element,
                        '.org-people-profile-card__profile-title, .org-people-profile-card__profile-name'
                    )
                    
                    title = await self._extract_text_from_element(
                        element,
                        '.org-people-profile-card__profile-info, .org-people-profile-card__profile-meta'
                    )
                    
                    profile_link = await element.query_selector('a[href*="/in/"]')
                    profile_url = None
                    if profile_link:
                        href = await profile_link.get_attribute('href')
                        if href:
                            profile_url = urljoin('https://www.linkedin.com', href)
                    
                    if name:
                        # Extract LinkedIn user ID from profile URL
                        linkedin_user_id = None
                        if profile_url:
                            match = re.search(r'/in/([^/]+)', profile_url)
                            if match:
                                linkedin_user_id = match.group(1)
                        
                        employees.append({
                            'linkedin_user_id': linkedin_user_id or f"user_{len(employees)}",
                            'name': name,
                            'title': title,
                            'profile_url': profile_url or ''
                        })
                
                except Exception as e:
                    logger.warning(f"Error extracting employee: {str(e)}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping employees: {str(e)}")
        
        return employees
    
    # Helper methods
    
    async def _extract_text(self, page: Page, selector: str) -> Optional[str]:
        """Extract text from first matching element"""
        try:
            element = await page.query_selector(selector)
            if element:
                return await element.inner_text()
        except:
            pass
        return None
    
    async def _extract_text_from_element(self, element: Any, selector: str) -> Optional[str]:
        """Extract text from element using selector"""
        try:
            sub_element = await element.query_selector(selector)
            if sub_element:
                return await sub_element.inner_text()
        except:
            pass
        return None
    
    async def _extract_attribute(self, page: Page, selector: str, attribute: str) -> Optional[str]:
        """Extract attribute from first matching element"""
        try:
            element = await page.query_selector(selector)
            if element:
                return await element.get_attribute(attribute)
        except:
            pass
        return None
    
    def _parse_number(self, text: str) -> Optional[int]:
        """Parse number from text (handles K, M suffixes)"""
        if not text:
            return None
        
        try:
            # Remove all non-numeric characters except K, M, and decimal point
            cleaned = re.sub(r'[^\d.KMkm]', '', text.strip())
            
            if 'K' in cleaned.upper() or 'k' in cleaned:
                number = float(re.sub(r'[^0-9.]', '', cleaned)) * 1000
                return int(number)
            elif 'M' in cleaned.upper() or 'm' in cleaned:
                number = float(re.sub(r'[^0-9.]', '', cleaned)) * 1000000
                return int(number)
            else:
                return int(re.sub(r'[^0-9]', '', cleaned))
        except:
            return None
    
    def _parse_relative_time(self, text: str) -> datetime:
        """Parse relative time string to datetime"""
        # Simple implementation - in production, use a proper library
        # For now, return current time
        return datetime.utcnow()
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create error response dictionary"""
        return {
            'error': True,
            'error_message': error_message,
            'page_info': None,
            'posts': [],
            'employees': [],
            'scraped_at': datetime.utcnow().isoformat()
        }

