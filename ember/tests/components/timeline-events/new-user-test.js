import { render } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';
import { module, test } from 'qunit';

import Service from '@ember/service';

import { setupRenderingTest } from '../../test-helpers';

module('Integration | Component | timeline events/new user', function (hooks) {
  setupRenderingTest(hooks);

  hooks.beforeEach(async function () {
    this.owner.setupRouter();

    this.owner.register(
      'service:account',
      Service.extend({
        user: null,
        club: null,
      }),
    );

    this.set('event', {
      time: '2016-06-24T12:34:56Z',
      actor: {
        id: 1,
        name: 'John Doe',
      },
    });

    await this.owner.lookup('service:intl').loadAndSetLocale('en');
  });

  test('renders default text', async function (assert) {
    await render(hbs`{{timeline-events/new-user event=event}}`);

    assert.dom('[data-test-text]').hasText('John Doe joined SkyLines.');
  });

  test('renders alternate text if actor is current user', async function (assert) {
    this.owner.lookup('service:account').set('user', { id: 1, name: 'John Doe' });

    await render(hbs`{{timeline-events/new-user event=event}}`);

    assert.dom('[data-test-text]').hasText('You joined SkyLines.');
  });
});
