const USERNAME = 'alice';
const PASSWORD = '123';
const TARGET_USER = 'bob';
const MESSAGE_TEXT = `Cypress message ${Date.now()}`;

function setCurrentUserNull() {
  cy.request('GET', '/api/state').then((response) => {
    expect(response.status).to.eq(200);

    const state = response.body || {};

    cy.request('POST', '/api/state', {
      ...state,
      currentUser: null
    }).then((postResponse) => {
      expect(postResponse.status).to.eq(200);
    });
  });
}

describe('Chat from one user to another', () => {
  it('logs in and sends a direct message', () => {
    setCurrentUserNull();

    cy.visit('/#/login');

    cy.get('#login-username').should('be.visible').clear().type(USERNAME);
    cy.get('#login-password').should('be.visible').clear().type(PASSWORD);
    cy.get('#login-form .auth-btn').click();

    cy.contains('.sidebar-tab', 'All Users').click();
    cy.contains('.list-item', 'Bob Jones').click();

    cy.get('#message-input').should('be.visible').clear().type(MESSAGE_TEXT);
    cy.get('.message-input-bar .fa-paper-plane').click();

    cy.contains('.message-list .msg-content', MESSAGE_TEXT).should('be.visible');

    cy.request('/api/state').then((response) => {
      expect(response.status).to.eq(200);
      const messages = response.body.messages || [];
      const savedMessage = messages.find((message) => {
        return (
          message.sender === USERNAME &&
          message.recipient === TARGET_USER &&
          message.type === 'direct' &&
          message.text === MESSAGE_TEXT
        );
      });

      expect(savedMessage, 'saved direct message').to.exist;
    });
  });
});