import os
import streamlit as st
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from typing import List, Dict, Optional, Any
from datetime import datetime
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseService:
    """MongoDB service for weather data persistence"""
    
    def __init__(self):
        try:
            self.mongodb_uri = st.secrets["MONGODB_URI"]
            self.database_name = st.secrets.get("DATABASE_NAME", "weather_app")
        except:
        
            self.mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
            self.database_name = os.getenv('DATABASE_NAME', 'weather_app')
        self.client = None
        self.db = None
        self.collection_name = 'weather_records'
        self.connected = False
        
        self._connect()
    
    def _connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(
                self.mongodb_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            self.connected = True
            
            # Create indexes for better performance
            self._create_indexes()
            
            st.success("✅ MongoDB connected successfully!")
            
        except ConnectionFailure as e:
            st.warning(f"⚠️ MongoDB connection failed: {e}. Using fallback storage.")
            self._init_fallback_storage()
        except Exception as e:
            st.warning(f"⚠️ Database error: {e}. Using fallback storage.")
            self._init_fallback_storage()
    
    def _init_fallback_storage(self):
        """Initialize session state fallback storage"""
        if 'weather_records' not in st.session_state:
            st.session_state.weather_records = []
        self.connected = False
    
    def _create_indexes(self):
        """Create database indexes"""
        if self.connected and self.db is not None:
            try:
                collection = self.db[self.collection_name]
                collection.create_index([('timestamp', -1)])
                collection.create_index([('location_name', 1)])
                collection.create_index([('latitude', 1), ('longitude', 1)])
            except Exception as e:
                print(f"Index creation error: {e}")
    
    def save_weather_record(self, weather_record: Dict[str, Any]) -> bool:
        """Save weather record to database"""
        try:
            if self.connected and self.db is not None:
                # MongoDB storage
                collection = self.db[self.collection_name]
                result = collection.insert_one(weather_record)
                return result.inserted_id is not None
            else:
                # Fallback to session state
                weather_record['_id'] = str(len(st.session_state.weather_records))
                st.session_state.weather_records.append(weather_record)
                return True
                
        except Exception as e:
            st.error(f"❌ Error saving weather record: {e}")
            return False
    
    def get_all_weather_records(self) -> List[Dict]:
        """Get all weather records"""
        try:
            if self.connected and self.db is not None:
                # MongoDB storage
                collection = self.db[self.collection_name]
                records = list(collection.find().sort('timestamp', -1))
                
                # Convert ObjectId to string for JSON serialization
                for record in records:
                    if '_id' in record:
                        record['_id'] = str(record['_id'])
                
                return records
            else:
                # Fallback to session state
                return st.session_state.get('weather_records', [])
                
        except Exception as e:
            st.error(f"❌ Error retrieving weather records: {e}")
            return []
    
    def get_weather_record_by_id(self, record_id: str) -> Optional[Dict]:
        """Get weather record by ID"""
        try:
            if self.connected and self.db is not None:
                # MongoDB storage
                collection = self.db[self.collection_name]
                record = collection.find_one({'_id': ObjectId(record_id)})
                
                if record:
                    record['_id'] = str(record['_id'])
                
                return record
            else:
                # Fallback to session state
                records = st.session_state.get('weather_records', [])
                for record in records:
                    if record.get('_id') == record_id:
                        return record
                return None
                
        except Exception as e:
            st.error(f"❌ Error retrieving weather record: {e}")
            return None
    
    def update_weather_record(self, record_id: str, update_data: Dict[str, Any]) -> bool:
        """Update weather record"""
        try:
            if self.connected and self.db is not None:
                # MongoDB storage
                collection = self.db[self.collection_name]
                update_data['updated_at'] = datetime.now()
                
                result = collection.update_one(
                    {'_id': ObjectId(record_id)},
                    {'$set': update_data}
                )
                
                return result.modified_count > 0
            else:
                # Fallback to session state
                records = st.session_state.get('weather_records', [])
                for i, record in enumerate(records):
                    if record.get('_id') == record_id:
                        records[i].update(update_data)
                        records[i]['updated_at'] = datetime.now()
                        return True
                return False
                
        except Exception as e:
            st.error(f"❌ Error updating weather record: {e}")
            return False
    
    def delete_weather_record(self, record_id: str) -> bool:
        """Delete weather record"""
        try:
            if self.connected and self.db is not None:
                # MongoDB storage
                collection = self.db[self.collection_name]
                result = collection.delete_one({'_id': ObjectId(record_id)})
                
                return result.deleted_count > 0
            else:
                # Fallback to session state
                records = st.session_state.get('weather_records', [])
                for i, record in enumerate(records):
                    if record.get('_id') == record_id:
                        del records[i]
                        return True
                return False
                
        except Exception as e:
            st.error(f"❌ Error deleting weather record: {e}")
            return False
    
    def get_records_by_location(self, location_name: str) -> List[Dict]:
        """Get records by location name"""
        try:
            if self.connected and self.db is not None:
                # MongoDB storage
                collection = self.db[self.collection_name]
                records = list(collection.find(
                    {'location_name': {'$regex': location_name, '$options': 'i'}}
                ).sort('timestamp', -1))
                
                for record in records:
                    record['_id'] = str(record['_id'])
                
                return records
            else:
                # Fallback to session state
                records = st.session_state.get('weather_records', [])
                filtered_records = [
                    record for record in records 
                    if location_name.lower() in record.get('location_name', '').lower()
                ]
                return filtered_records
                
        except Exception as e:
            st.error(f"❌ Error retrieving records by location: {e}")
            return []
    
    def get_records_by_date_range(self, start_date, end_date) -> List[Dict]:
        """Get records within date range"""
        try:
            if self.connected and self.db is not None:
                # MongoDB storage
                collection = self.db[self.collection_name]
                records = list(collection.find({
                    'timestamp': {
                        '$gte': start_date,
                        '$lte': end_date
                    }
                }).sort('timestamp', -1))
                
                for record in records:
                    record['_id'] = str(record['_id'])
                
                return records
            else:
                # Fallback to session state
                records = st.session_state.get('weather_records', [])
                filtered_records = []
                
                for record in records:
                    record_date = record.get('timestamp')
                    if isinstance(record_date, datetime):
                        if start_date <= record_date.date() <= end_date:
                            filtered_records.append(record)
                
                return filtered_records
                
        except Exception as e:
            st.error(f"❌ Error retrieving records by date range: {e}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            if self.connected and self.db is not None:
                # MongoDB statistics
                collection = self.db[self.collection_name]
                total_records = collection.count_documents({})
                
                # Get unique locations
                unique_locations = len(collection.distinct('location_name'))
                
                # Get date range
                oldest_record = collection.find().sort('timestamp', 1).limit(1)
                newest_record = collection.find().sort('timestamp', -1).limit(1)
                
                oldest_date = None
                newest_date = None
                
                oldest_list = list(oldest_record)
                newest_list = list(newest_record)
                
                if oldest_list:
                    oldest_date = oldest_list[0].get('timestamp')
                if newest_list:
                    newest_date = newest_list[0].get('timestamp')
                
                return {
                    'total_records': total_records,
                    'unique_locations': unique_locations,
                    'oldest_record': oldest_date,
                    'newest_record': newest_date,
                    'storage_type': 'MongoDB',
                    'connected': True
                }
            else:
                # Session state statistics
                records = st.session_state.get('weather_records', [])
                unique_locations = len(set(record.get('location_name', '') for record in records))
                
                return {
                    'total_records': len(records),
                    'unique_locations': unique_locations,
                    'oldest_record': None,
                    'newest_record': None,
                    'storage_type': 'Session Storage',
                    'connected': False
                }
                
        except Exception as e:
            st.error(f"❌ Error getting database stats: {e}")
            return {
                'total_records': 0,
                'unique_locations': 0,
                'oldest_record': None,
                'newest_record': None,
                'storage_type': 'Error',
                'connected': False
            }
    
    def close_connection(self):
        """Close database connection"""
        try:
            if self.client is not None:
                self.client.close()
                self.connected = False
        except Exception as e:
            print(f"Error closing database connection: {e}")
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            if self.connected and self.db is not None:
                self.client.admin.command('ping')
                return True
            else:
                return False
        except Exception:
            return False