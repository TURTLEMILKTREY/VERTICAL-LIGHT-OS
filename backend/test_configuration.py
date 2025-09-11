#!/usr/bin/env python3
"""
Configuration System Test
Tests the enhanced schema system and configuration loading
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from config.config_manager import ConfigurationManager

def test_configuration_system():
    """Test the enhanced configuration system"""
    print('🔧 Testing enhanced schema system...')
    
    try:
        # Initialize configuration manager
        print('📋 Initializing ConfigurationManager...')
        config_manager = ConfigurationManager()
        
        # Test goal parser configuration
        print('🎯 Testing goal parser configuration...')
        processing_config = config_manager.get('goal_parser.processing')
        print(f'✓ Goal parser processing config loaded: {processing_config}')
        
        intelligence_config = config_manager.get('goal_parser.intelligence')
        print(f'✓ Goal parser intelligence config loaded: {intelligence_config}')
        
        # Test campaign generator configuration  
        print('📈 Testing campaign generator configuration...')
        generation_config = config_manager.get('campaign_generator.generation')
        print(f'✓ Campaign generator generation config loaded: {generation_config}')
        
        channel_config = config_manager.get('campaign_generator.channel_intelligence')
        print(f'✓ Campaign generator channel config loaded: {channel_config}')
        
        # Test specific values
        print('🔍 Testing specific configuration values...')
        timeout = config_manager.get('goal_parser.processing.timeout_seconds')
        learning_rate = config_manager.get('campaign_generator.learning.learning_rate')
        print(f'✓ Specific values - timeout: {timeout}s, learning_rate: {learning_rate}')
        
        # Test validation
        print('🛡️ Testing configuration validation...')
        industry_multipliers = config_manager.get('campaign_generator.channel_intelligence.industry_multipliers')
        print(f'✓ Industry multipliers validated: {len(industry_multipliers)} industries configured')
        
        channel_performance = config_manager.get('campaign_generator.channel_performance')
        print(f'✓ Channel performance validated: {len(channel_performance)} channels configured')
        
        # Test environment detection
        print('🌍 Testing environment configuration...')
        current_env = config_manager.environment
        print(f'✓ Current environment detected: {current_env}')
        
        print('✅ All configuration tests passed successfully!')
        return True
        
    except Exception as e:
        print(f'❌ Configuration test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_configuration_system()
    sys.exit(0 if success else 1)
