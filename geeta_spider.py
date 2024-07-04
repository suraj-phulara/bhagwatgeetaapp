import scrapy

class GitaSpider(scrapy.Spider):
    name = 'gita'
    
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'gita_verses.csv',
        'FEED_EXPORT_FIELDS': ['id', 'chapter', 'verse', 'verse_text', 'translation', 'commentary']
    }

    def __init__(self, *args, **kwargs):
        super(GitaSpider, self).__init__(*args, **kwargs)
        self.start_urls = [f'https://www.holy-bhagavad-gita.org/chapter/{chapter}/verse/{verse}' 
                           for chapter in range(1, 19) 
                           for verse in range(1, self.get_verse_count(chapter) + 1)]
        self.current_id = 1
    
    def get_verse_count(self, chapter):
        # Verse counts for each chapter of the Bhagavad Gita
        verse_counts = {
            1: 47, 2: 72, 3: 43, 4: 42, 5: 29, 6: 47, 7: 30, 8: 28, 9: 34,
            10: 42, 11: 55, 12: 20, 13: 34, 14: 27, 15: 20, 16: 24, 17: 28, 18: 78
        }
        return verse_counts.get(chapter, 0)
    
    def parse(self, response):
        chapter = response.url.split('/')[-3]
        verse = response.url.split('/')[-1]
        verse_text = response.xpath('//div[@id="originalVerse"]/p/text()').getall()
        translation = response.xpath('//div[@id="translation"]/p/text()').getall()
        commentary = response.xpath('//div[@id="commentary"]/p/text()').getall()
        
        # Yielding the data with an incremental id
        yield {
            'id': self.current_id,
            'chapter': chapter,
            'verse': verse,
            'verse_text': ' '.join(verse_text),
            'translation': ' '.join(translation),
            'commentary': ' '.join(commentary)
        }
        
        # Incrementing the id for the next verse
        self.current_id += 1
