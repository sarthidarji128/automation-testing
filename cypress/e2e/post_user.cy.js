describe('POST User API Test', () => {
  it('successfully creates a new user via signup', () => {
    // Reset currentUser to signup
    cy.request('GET', '/api/state').then((response) => {
      const state = response.body || {};
      cy.request('POST', '/api/state', { ...state, currentUser: null });
    });

    const uniqueId = Date.now().toString().substr(-6);
    const username = `user_${uniqueId}`;
    const name = `Test User ${uniqueId}`;

    cy.visit('/#/signup');
    cy.get('#signup-name').should('be.visible').clear().type(name);
    cy.get('#signup-username').should('be.visible').clear().type(username);
    cy.get('#signup-password').should('be.visible').clear().type('123456');
    cy.get('#signup-form .auth-btn').click();

    // Verify chat page is loaded after successful POST /api/users signup
    cy.url().should('include', '/#/chat');
    cy.get('.sidebar').should('be.visible');

    // Verify user is in db
    cy.request('/api/state').then((response) => {
      const users = response.body.users || [];
      const user = users.find(u => u.username === username);
      expect(user).to.exist;
      expect(user.name).to.equal(name);
    });
  });
});
