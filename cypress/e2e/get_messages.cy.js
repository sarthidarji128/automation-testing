describe('GET Messages API Test', () => {
  it('successfully fetches and renders direct chat history', () => {
    cy.request('GET', '/api/state').then((response) => {
      const state = response.body || {};
      cy.request('POST', '/api/state', { ...state, currentUser: null });
    });

    cy.visit('/#/login');
    cy.get('#login-username').should('be.visible').clear().type('alice');
    cy.get('#login-password').should('be.visible').clear().type('123');
    cy.get('#login-form .auth-btn').click();

    cy.url().should('include', '/#/chat');
    
    // Switch to Users list to click Bob
    cy.get('#tab-users').should('be.visible').click();
    cy.get('.list-item').contains('Bob').click();

    // Verify chat area is updated (calls GET /api/messages?chatWith=bob)
    cy.get('.chat-title').should('contain', 'Bob');
    cy.get('.message-list').should('be.visible');
  });
});
