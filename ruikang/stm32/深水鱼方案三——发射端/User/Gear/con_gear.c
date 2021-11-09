#include "con_gear.h"
#include "bsp_GeneralTim.h"
#include "bsp_usart.h"

uint32_t RUDDER_ROTATE_DELAY = 180;																									//����任������
uint32_t CCR_theta = 750;																														//�������CCR
uint32_t theta_amplitude = 18;																											//��������˶���ֵ����ÿ1.8��ռ�ձ�ռ��0.1%��CCRռ��10
uint32_t CCR_theta_F = 750;//CCR_theta;
uint32_t CCR_theta_H = 850;//CCR_theta + 10 * theta_amplitude / 1.8;
uint32_t CCR_theta_L = 650;//CCR_theta - 10 * theta_amplitude / 1.8;

/**CCRװ��ģ��
	*���幦�ܣ���ʼ��PWMռ�ձȵ���Сֵ�����ֵ
	*���������
	*���ز�����
	*�漰������
	**CCR_theta_H��CCR_theta_F��theta_amplitude�޸�
	**CCR_theta_L��CCR_theta_F��theta_amplitude�޸�
	*/
void CCR_Put_in(void)
{
	CCR_theta_H = CCR_theta_F+10*theta_amplitude/1.8;
	CCR_theta_L = CCR_theta_F-10*theta_amplitude/1.8;
}

void Gear_Control(uint8_t num)
{
	switch(num)
	{
		case 0:{TIM_Cmd(GENERAL_TIM2, DISABLE);}break;//stop
		case 1:{TIM_Cmd(GENERAL_TIM2, ENABLE);CCR_theta_F = CCR_theta;CCR_Put_in();}break;//move
		case 2:{CCR_theta_F = CCR_theta - 200;CCR_Put_in();}break;//left4
		case 3:{CCR_theta_F = CCR_theta - 100;CCR_Put_in();}break;//left1
		case 4:{CCR_theta_F = CCR_theta + 100;CCR_Put_in();}break;//right1
		case 5:{CCR_theta_F = CCR_theta + 200;CCR_Put_in();}break;//right4
	}
}
/*********************************************END OF FILE**********************/
