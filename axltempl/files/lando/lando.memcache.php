
// Memcache settings
$memcache_exists = class_exists('Memcache', FALSE);
$memcached_exists = class_exists('Memcached', FALSE);
if ($memcache_exists || $memcached_exists) {
  $settings['memcache']['servers'] = [
    $lando_info['cache']['internal_connection']['host'] . ':' . $lando_info['cache']['internal_connection']['port'] => 'default',
  ];

  $class_loader->addPsr4('Drupal\\memcache\\', 'modules/contrib/memcache/src');

  // Define custom bootstrap container definition to use Memcache for cache.container.
  $settings['bootstrap_container_definition'] = [
    'parameters' => [],
    'services' => [
      # Dependencies.
      'settings' => [
        'class' => 'Drupal\Core\Site\Settings',
        'factory' => 'Drupal\Core\Site\Settings::getInstance',
      ],
      'memcache.settings' => [
        'class' => 'Drupal\memcache\MemcacheSettings',
        'arguments' => ['@settings'],
      ],
      'memcache.factory' => [
        'class' => 'Drupal\memcache\Driver\MemcacheDriverFactory',
        'arguments' => ['@memcache.settings'],
      ],
      'memcache.timestamp.invalidator.bin' => [
        'class' => 'Drupal\memcache\Invalidator\MemcacheTimestampInvalidator',
        # Adjust tolerance factor as appropriate when not running memcache on localhost.
        'arguments' => ['@memcache.factory', 'memcache_bin_timestamps', 0.001],
      ],
      'memcache.timestamp.invalidator.tag' => [
        'class' => 'Drupal\memcache\Invalidator\MemcacheTimestampInvalidator',
        # Remember to update your main service definition in sync with this!
        # Adjust tolerance factor as appropriate when not running memcache on localhost.
        'arguments' => ['@memcache.factory', 'memcache_tag_timestamps', 0.001],
      ],
      'memcache.backend.cache.container' => [
        'class' => 'Drupal\memcache\DrupalMemcacheInterface',
        'factory' => ['@memcache.factory', 'get'],
        # Actual cache bin to use for the container cache.
        'arguments' => ['container'],
      ],
      # Define a custom cache tags invalidator for the bootstrap container.
      'cache_tags_provider.container' => [
        'class' => 'Drupal\memcache\Cache\TimestampCacheTagsChecksum',
        'arguments' => ['@memcache.timestamp.invalidator.tag'],
      ],
      'cache.container' => [
        'class' => 'Drupal\memcache\MemcacheBackend',
        'arguments' => ['container', '@memcache.backend.cache.container', '@cache_tags_provider.container', '@memcache.timestamp.invalidator.bin'],
      ],
    ],
  ];
}
