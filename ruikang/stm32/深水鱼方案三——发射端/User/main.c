#include "stm32f10x.h"
#include "bsp_gpio.h"
#include "bsp_GeneralTim.h"
#include "bsp_usart.h"


#include <stdio.h>
#include <string.h>

uint16_t time = 0xFFFF;																															//ʱ�����

//GPIO������
#define KEY1 PAin(0)
#define KEY2 PCin(13)
#define KEY3 PCin(4)
#define KEY4 PCin(5)
#define LED_R PBout(5)
#define LED_G PBout(0)
#define LED_B PBout(1)

uint16_t volatile CCR1_Val = 750;
uint16_t volatile CCR2_Val = 750;

extern uint8_t config_complete[Array_Length];																				//��ʼ�����
extern uint8_t self_check_enable;																										//��ʼ��������
extern uint32_t watchdog_delay;
extern uint8_t sleep_warning[Array_Length];																					//���߾���

void Delay(__IO u32 nCount);

/**
  * @brief  ������
  * @param  ��  
  * @retval ��
  */
int main(void)
{
	GPIO_Config();																																		//��ʼ��GPIO				����ģʽΪ ����
	USART_Config();																																		//��ʼ��USART			����ģʽΪ 115200 8-N-1���жϽ���
	USART2_Config();
	USART3_Config();
	GENERAL_TIM_Init();																																//��ʼ��˫·TIM   	����ģʽΪ ���ø������
	TIM_Cmd(GENERAL_TIM2, DISABLE);
	while(1)
	{
		if(watchdog_delay > 30000)
		{
			Usart_SendArray(USART2,sleep_warning,Array_Length);
			while(watchdog_delay > 30000);
		}
			
	}
}

/**�ӳٷ�����
	*���幦�ܣ����ӳ�
	*���������һ��32λ����
	*���ز�����
	*�漰������
	*/
void Delay(__IO uint32_t nCount)
{
	for(; nCount != 0; nCount--);
}

/*********************************************END OF FILE**********************/
