const USERNAME = 'alice';
const PASSWORD = '123';
const GROUP_NAME = 'Cypress All Users Group';

function resetCurrentUser() {
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

function loginAsAlice() {
  cy.visit('/#/login');

  cy.get('#login-username').should('be.visible').clear().type(USERNAME);
  cy.get('#login-password').should('be.visible').clear().type(PASSWORD);
  cy.get('#login-form .auth-btn').click();
}

describe('Create a group with all users', () => {
  it('logs in, creates a group, and includes every member', () => {
    resetCurrentUser();
    loginAsAlice();

    cy.get('.sidebar-actions [title="Create Group"]').click({ force: true });

    cy.get('#group-name').should('be.visible').clear().type(GROUP_NAME);
    cy.get('input[name="group_member"]').should('have.length.at.least', 1).check({ force: true });
    cy.contains('.modal-btn.confirm', 'Create Group').click();

    cy.contains('.item-name', GROUP_NAME).should('be.visible');

    cy.request('/api/state').then((response) => {
      expect(response.status).to.eq(200);

      const state = response.body || {};
      const users = state.users || [];
      const groups = state.groups || [];
      const createdGroup = groups.find((group) => group.name === GROUP_NAME);

      expect(createdGroup, 'created group').to.exist;
      expect(createdGroup.members, 'group members').to.deep.equal(
        users.map((user) => user.username)
      );
    });
  });
});